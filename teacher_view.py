# ============================================================
# teacher_view.py — Öğretmen Yönetim Paneli
# ============================================================

import streamlit as st
import json
import time
import os
import io
from datetime import datetime
from dotenv import load_dotenv
from db_utils import (
    get_all_students_with_results, reset_database,
    delete_specific_students, save_holistic_analysis,
    get_student_analysis_history, is_using_sqlite
)

load_dotenv()

DEFAULT_MODEL = "claude-sonnet-4-20250514"
def _get_claude_model():
    try:
        if "CLAUDE_MODEL" in st.secrets: return st.secrets["CLAUDE_MODEL"]
    except: pass
    return os.getenv("CLAUDE_MODEL", DEFAULT_MODEL)

def get_claude_client():
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
        else:
            api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key: return None
        from anthropic import Anthropic
        return Anthropic(api_key=api_key)
    except:
        return None

def get_ai_analysis(prompt):
    client = get_claude_client()
    if not client:
        return "⚠️ Claude API Key bulunamadı."
    try:
        response = client.messages.create(
            model=_get_claude_model(), max_tokens=16000,
            temperature=0.3, messages=[{"role": "user", "content": prompt}])
        return response.content[0].text
    except Exception as e:
        return f"⚠️ Hata: {e}"


def app():
    st.markdown("## 👨‍🏫 Öğretmen Yönetim Paneli")
    st.caption("Okuma Analiz Merkezi — Test Sonuçları ve AI Raporları")

    if st.button("🚪 Giriş Ekranına Dön", key="teacher_back"):
        st.session_state.clear()
        st.rerun()

    if is_using_sqlite():
        st.warning("⚠️ SQLite kullanılıyor. Kalıcı veri için SUPABASE_DB_URL ekleyin.")

    st.markdown("---")
    data = get_all_students_with_results()
    student_names = [d["info"].name for d in data] if data else []

    # Sidebar yönetim
    with st.sidebar:
        st.markdown("### ⚙️ Yönetim")
        with st.expander("🗑️ Öğrenci Sil"):
            if student_names:
                selected_del = st.multiselect("Seçin:", student_names)
                if selected_del and st.button("SİL", type="primary"):
                    if delete_specific_students(selected_del):
                        st.success("Silindi!")
                        time.sleep(1)
                        st.rerun()
        with st.expander("⚠️ Sistemi Sıfırla"):
            st.error("Tüm veri silinir!")
            if st.checkbox("Onaylıyorum"):
                if st.button("SIFIRLA", type="primary"):
                    if reset_database():
                        st.success("Sıfırlandı!")
                        time.sleep(1)
                        st.rerun()

    if not data:
        st.info("📂 Henüz kayıtlı öğrenci yok.")
        return

    # İstatistikler
    total_students = len(data)
    total_tests = sum(len(d["tests"]) for d in data)
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("👥 Toplam Öğrenci", total_students)
    mc2.metric("📝 Toplam Test", total_tests)
    mc3.metric("📊 Ort. Test/Öğrenci", round(total_tests/total_students, 1) if total_students else 0)

    st.markdown("---")

    # Öğrenci seçimi
    selected_name = st.selectbox("📂 Öğrenci Seç:", student_names, index=None, placeholder="Bir öğrenci seçin...")
    if not selected_name:
        st.info("👆 Öğrenci seçin.")
        return

    student_data = next(d for d in data if d["info"].name == selected_name)
    info = student_data["info"]
    tests = student_data["tests"]

    st.markdown(f"### 📁 {info.name} — Öğrenci Dosyası")

    tab_profil, tab_testler, tab_ai = st.tabs(["📋 Profil", "📝 Test Sonuçları", "🤖 AI Raporları"])

    with tab_profil:
        grade_text = f"{info.grade}. Sınıf" if info.grade else "—"
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown(f"""
            | | |
            |---|---|
            | **Ad Soyad** | {info.name} |
            | **Yaş** | {info.age} |
            | **Cinsiyet** | {info.gender} |
            | **Sınıf** | {grade_text} |
            | **E-posta** | {info.username} |
            """)
        with col_r:
            st.metric("🔑 Giriş", info.login_count)
            st.metric("📊 Test", len(tests))

    with tab_testler:
        if not tests:
            st.warning("Henüz test çözülmemiş.")
        else:
            for idx, t in enumerate(tests):
                with st.expander(f"✅ {t['test_name']} ({t['date']})"):
                    # Skor gösterimi
                    if t['scores']:
                        scores = t['scores']
                        if "dogruluk_yuzdesi" in scores:
                            st.metric("Doğruluk", f"%{scores['dogruluk_yuzdesi']}")
                        if "toplam_hata" in scores:
                            st.metric("Toplam Hata", scores['toplam_hata'])
                        if "hata_dagilimi" in scores and isinstance(scores['hata_dagilimi'], dict):
                            st.markdown("**Hata Dağılımı:**")
                            for k, v in scores['hata_dagilimi'].items():
                                if v > 0:
                                    st.write(f"- {k}: {v}")
                        if "wpm" in scores:
                            st.metric("Okuma Hızı", f"{scores['wpm']} kel/dk")

                    st.markdown("### 📄 Rapor")
                    if t.get('report'):
                        st.markdown(t['report'])
                    else:
                        st.warning("Rapor bulunamadı.")

    with tab_ai:
        history = get_student_analysis_history(info.id)
        if history:
            st.markdown(f"**{len(history)} kayıtlı rapor**")
            for idx, record in enumerate(history):
                with st.expander(f"🤖 {record['combination']} ({record['date']})"):
                    st.markdown(record['report'])
        else:
            st.info("Henüz AI raporu yok.")

        st.divider()
        st.subheader("⚡ Yeni AI Analizi")
        if tests:
            test_names = [t["test_name"] for t in tests]
            selected_tests = st.multiselect("Test Seç:", test_names, default=test_names)
            if selected_tests and st.button("🚀 ANALİZ BAŞLAT", type="primary"):
                analyzed = [t for t in tests if t["test_name"] in selected_tests]
                ai_input = []
                for t in analyzed:
                    raw = t.get("raw_answers", "")
                    if isinstance(raw, str):
                        try: raw = json.loads(raw)
                        except: pass
                    ai_input.append({"TEST_ADI": t["test_name"], "TARİH": str(t["date"]),
                                     "SONUÇLAR": t["scores"] if t["scores"] else raw})

                grade_text = f"{info.grade}. Sınıf" if info.grade else "Belirtilmemiş"
                prompt = f"""Sen deneyimli bir okuma uzmanısın. Aşağıdaki öğrencinin test sonuçlarını analiz et.

Öğrenci: {info.name}, Yaş: {info.age}, Sınıf: {grade_text}, Cinsiyet: {info.gender}

Test Verileri:
```json
{json.dumps(ai_input, ensure_ascii=False, indent=2)}
```

Lütfen kapsamlı bir analiz raporu oluştur:
1. Genel değerlendirme ve profil
2. Güçlü yönler
3. Gelişim alanları
4. Öğrenci, aile ve öğretmen için öneriler
5. Egzersiz planı
6. Takip önerileri

Rapor profesyonel, yapıcı ve detaylı olmalı. Türkçe yaz. En az 2000 kelime."""

                with st.spinner("AI analiz hazırlıyor..."):
                    report = get_ai_analysis(prompt)
                    save_holistic_analysis(info.id, selected_tests, report)
                    st.success("✅ Analiz tamamlandı!")
                    time.sleep(1.5)
                    st.rerun()

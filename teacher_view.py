"""
Öğretmen Paneli
— Öğrenci yönetimi, ses kaydı dinleme, Claude AI ile analiz
"""

import streamlit as st
import base64
from db_utils import (
    get_all_students, get_user_by_id, get_recordings_by_user,
    get_recording_by_id, save_analysis_report, get_report_by_recording,
    get_reports_by_user, get_speed_reading_results
)
from okuma_hata_engine import analyze_reading_with_claude, HATA_KATEGORILERI


def render_teacher_view():
    """Öğretmen panelini render eder."""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); 
                padding: 1.5rem 2rem; border-radius: 16px; margin-bottom: 2rem; color: white;">
        <h2 style="margin:0; color:white;">🏫 Öğretmen Paneli</h2>
        <p style="margin:0.5rem 0 0 0; opacity:0.85;">Okuma Hata Analizi Yönetim Merkezi</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👨‍🎓 Öğrenci Analizi", "📊 Genel Bakış", "📚 Hata Kategorileri"])
    
    with tab1:
        render_ogrenci_analizi()
    
    with tab2:
        render_genel_bakis()
    
    with tab3:
        render_hata_kategorileri()


def render_ogrenci_analizi():
    """Öğrenci seçimi ve analiz arayüzü."""
    students = get_all_students()
    
    if not students:
        st.info("📭 Henüz kayıtlı öğrenci bulunmuyor.")
        return
    
    # Öğrenci seçimi
    st.markdown("### 👨‍🎓 Öğrenci Seçimi")
    
    # Sınıfa göre grupla
    grades = sorted(set(s['grade'] for s in students))
    selected_grade = st.selectbox("📚 Sınıf Filtresi", ["Tümü"] + [f"{g}. Sınıf" for g in grades])
    
    if selected_grade != "Tümü":
        grade_num = int(selected_grade.split(".")[0])
        filtered = [s for s in students if s['grade'] == grade_num]
    else:
        filtered = students
    
    # Öğrenci listesi
    student_options = {f"{s['name']} ({s['grade']}. Sınıf) — {s['email']}": s['id'] for s in filtered}
    
    if not student_options:
        st.info("Bu sınıfta kayıtlı öğrenci yok.")
        return
    
    selected_name = st.selectbox("👤 Öğrenci Seç", list(student_options.keys()))
    selected_id = student_options[selected_name]
    student = get_user_by_id(selected_id)
    
    if not student:
        st.error("Öğrenci bulunamadı.")
        return
    
    # Öğrenci bilgi kartı
    st.markdown(f"""
    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.2rem; margin: 1rem 0;">
        <div style="display:flex; gap: 2rem; flex-wrap: wrap;">
            <div><strong>👤 Ad:</strong> {student['name']}</div>
            <div><strong>📚 Sınıf:</strong> {student['grade']}. Sınıf</div>
            <div><strong>🎂 Yaş:</strong> {student['age']}</div>
            <div><strong>⚧ Cinsiyet:</strong> {student['gender']}</div>
            <div><strong>📧 E-posta:</strong> {student['email']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Ses kayıtları
    st.markdown("### 🎤 Ses Kayıtları")
    recordings = get_recordings_by_user(selected_id)
    
    if not recordings:
        st.info("Bu öğrencinin henüz ses kaydı bulunmuyor.")
        return
    
    for rec in recordings:
        rec_id = rec['id']
        existing_report = get_report_by_recording(rec_id)
        
        status_badge = "✅ Analiz Yapıldı" if existing_report else "⏳ Analiz Bekliyor"
        status_color = "#10B981" if existing_report else "#F59E0B"
        
        with st.expander(f"📅 {rec['created_at']} — {rec['text_id']}  |  {status_badge}", expanded=not existing_report):
            # Orijinal metin
            with st.container():
                st.markdown("**📄 Orijinal Metin:**")
                st.markdown(f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; 
                            padding: 1rem; font-size: 0.95rem; line-height: 1.7; max-height: 200px; overflow-y: auto;">
                    {rec['original_text']}
                </div>
                """, unsafe_allow_html=True)
            
            # Ses kaydını dinle
            st.markdown("**🔊 Ses Kaydı:**")
            full_rec = get_recording_by_id(rec_id)
            if full_rec and full_rec.get('audio_base64'):
                try:
                    audio_bytes = base64.b64decode(full_rec['audio_base64'])
                    st.audio(audio_bytes, format="audio/wav")
                except Exception as e:
                    st.error(f"Ses kaydı oynatılamadı: {e}")
            else:
                st.warning("Ses kaydı verisi bulunamadı.")
            
            # Analiz butonu veya mevcut rapor
            if existing_report:
                st.markdown("### 📋 Analiz Raporu")
                st.markdown(existing_report['report_markdown'])
                st.markdown(f"<small style='color: #94A3B8;'>📅 Rapor tarihi: {existing_report['created_at']}</small>", unsafe_allow_html=True)
                
                # Yeniden analiz
                if st.button(f"🔄 Yeniden Analiz Et", key=f"reanalyze_{rec_id}"):
                    run_analysis(rec_id, selected_id, student, full_rec)
            else:
                if st.button(f"🤖 Claude AI ile Analiz Et", key=f"analyze_{rec_id}", type="primary"):
                    run_analysis(rec_id, selected_id, student, full_rec)
    
    # Hızlı okuma sonuçları
    st.markdown("### ⚡ Hızlı Okuma Sonuçları")
    speed_results = get_speed_reading_results(selected_id)
    if speed_results:
        for r in speed_results:
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("📚 Sınıf", f"{r['grade']}. Sınıf")
            with col2:
                st.metric("⚡ Hız", f"{r['wpm']:.0f} k/dk")
            with col3:
                st.metric("🎯 Anlama", f"%{r['comprehension_pct']:.0f}")
            with col4:
                st.metric("📈 Etkili Hız", f"{r['effective_speed']:.0f}")
            with col5:
                st.metric("✅ Doğru", f"{r['correct_answers']}/{r['total_questions']}")
            st.markdown(f"<small style='color: #94A3B8;'>📅 {r['created_at']}</small>", unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.info("Bu öğrencinin hızlı okuma test sonucu bulunmuyor.")


def run_analysis(rec_id, student_id, student, full_rec):
    """Claude AI analizi çalıştırır."""
    if not full_rec or not full_rec.get('audio_base64'):
        st.error("Ses kaydı verisi bulunamadı!")
        return
    
    with st.spinner("🤖 Claude AI analiz yapıyor... Bu işlem 30-60 saniye sürebilir."):
        progress = st.progress(0)
        progress.progress(10, "Ses kaydı hazırlanıyor...")
        
        report = analyze_reading_with_claude(
            audio_base64=full_rec['audio_base64'],
            original_text=full_rec['original_text'],
            student_name=student['name'],
            student_grade=student['grade'],
            audio_format="wav"
        )
        
        progress.progress(80, "Rapor kaydediliyor...")
        
        if report and not report.startswith("❌"):
            save_analysis_report(
                recording_id=rec_id,
                user_id=student_id,
                report_markdown=report,
            )
            progress.progress(100, "Tamamlandı!")
            st.success("✅ Analiz tamamlandı ve kaydedildi!")
            st.markdown("### 📋 Analiz Raporu")
            st.markdown(report)
        else:
            progress.progress(100, "Hata!")
            st.error(report or "Bilinmeyen bir hata oluştu.")


def render_genel_bakis():
    """Tüm öğrencilerin genel durumu."""
    st.markdown("### 📊 Genel Bakış")
    
    students = get_all_students()
    if not students:
        st.info("Kayıtlı öğrenci bulunmuyor.")
        return
    
    # İstatistikler
    total_students = len(students)
    grades = {}
    for s in students:
        g = s['grade']
        grades[g] = grades.get(g, 0) + 1
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👨‍🎓 Toplam Öğrenci", total_students)
    with col2:
        st.metric("📚 Sınıf Sayısı", len(grades))
    with col3:
        total_recordings = sum(len(get_recordings_by_user(s['id'])) for s in students)
        st.metric("🎤 Toplam Kayıt", total_recordings)
    
    # Sınıf bazlı dağılım
    st.markdown("#### 📚 Sınıf Bazlı Öğrenci Dağılımı")
    for g in sorted(grades.keys()):
        st.markdown(f"**{g}. Sınıf:** {grades[g]} öğrenci")
    
    # Öğrenci listesi tablosu
    st.markdown("#### 👥 Öğrenci Listesi")
    table_data = []
    for s in students:
        recs = get_recordings_by_user(s['id'])
        speed_results = get_speed_reading_results(s['id'])
        table_data.append({
            "Ad": s['name'],
            "Sınıf": f"{s['grade']}. Sınıf",
            "Yaş": s['age'],
            "Ses Kayıtları": len(recs),
            "Hızlı Okuma Testleri": len(speed_results),
            "Kayıt Tarihi": s['created_at'],
        })
    
    if table_data:
        st.dataframe(table_data, use_container_width=True)


def render_hata_kategorileri():
    """Hata kategorilerini gösterir."""
    st.markdown("### 📚 Okuma Hata Kategorileri")
    st.markdown("Bu 10 kategori, öğrencinin sesli okuma performansını değerlendirmek için kullanılır:")
    
    for k in HATA_KATEGORILERI:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; 
                    padding: 1rem 1.2rem; margin: 0.5rem 0;">
            <div style="font-size: 1.1rem; font-weight: 600; color: #1E293B;">
                {k['emoji']} {k['id']}. {k['ad']}
            </div>
            <div style="color: #64748B; margin-top: 0.3rem;">{k['aciklama']}</div>
        </div>
        """, unsafe_allow_html=True)

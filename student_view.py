# ============================================================
# student_view.py — Öğrenci Test Arayüzü v2.0
# Ses Kaydı → Claude API Ses Analizi → Hata Raporu
# ============================================================

import streamlit as st
import streamlit.components.v1 as components
import time
import json
import base64
import os
from db_utils import save_test_result_to_db, get_completed_tests
from okuma_hata_engine import (
    get_metin_for_grade, count_words, classify_reading_speed,
    build_okuma_hata_prompt, parse_ai_response,
    get_performance_level, generate_summary_report,
    HATA_KATEGORILERI, OKUMA_HIZI_NORMLARI,
)
from hizli_okuma_engine import (
    get_passage_for_grade, count_words as ho_count_words,
    calculate_speed_reading, generate_speed_reading_report,
)


# ============================================================
# CLAUDE API
# ============================================================
def get_claude_client():
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
        else:
            api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return None
        from anthropic import Anthropic
        return Anthropic(api_key=api_key)
    except Exception:
        return None


def get_claude_model():
    try:
        if "CLAUDE_MODEL" in st.secrets:
            return st.secrets["CLAUDE_MODEL"]
    except Exception:
        pass
    return os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")


def analyze_audio_with_claude(audio_bytes, audio_format, original_text, grade,
                               student_name="", student_age=None, reading_time_seconds=None):
    """Ses kaydini + orijinal metni Claude'a gonder. Tek cagrida transkripsiyon + analiz."""
    client = get_claude_client()
    if not client:
        return None, "Claude API Key bulunamadi."

    mime_map = {
        "wav": "audio/wav", "webm": "audio/webm", "mp3": "audio/mpeg",
        "mp4": "audio/mp4", "m4a": "audio/mp4", "ogg": "audio/ogg",
    }
    mime_type = mime_map.get(audio_format, "audio/wav")
    audio_b64 = base64.standard_b64encode(audio_bytes).decode("utf-8")

    word_count = count_words(original_text)
    wpm = None
    speed_info = ""
    if reading_time_seconds and reading_time_seconds > 0:
        wpm = round(word_count / (reading_time_seconds / 60))
        speed_key, speed_label, speed_emoji = classify_reading_speed(wpm, grade)
        speed_info = f"\n- Okuma hizi: {wpm} kelime/dakika ({speed_emoji} {speed_label})"

    prompt_text = f"""# ROL
Sen Turkiye'nin en deneyimli okuma uzmanisin.

# GOREV
Ses kaydini dinle, ogrencinin sesli okumasini orijinal metinle karsilastir, kapsamli hata analizi yap.

# BILGILER
- Sinif: {grade}. Sinif
- Kelime sayisi: {word_count}{speed_info}
- Ogrenci: {student_name or 'Belirtilmemis'}

# ORIJINAL METIN
```
{original_text}
```

# TALIMATLAR

1. Ses kaydini dinle, ogrencinin soyledigi her kelimeyi AYNEN transkribe et
2. Orijinal metinle karsilastir
3. Hatalari kategorize et:
   - harf_hatasi: Harflerin yanlis okunmasi
   - hece_hatasi: Hecelerin yanlis bolunmesi
   - kelime_hatasi: Kelimenin tamamen farkli okunmasi
   - atlama_hatasi: Kelime/satir atlanmasi
   - ekleme_hatasi: Metinde olmayan kelime eklenmesi
   - tekrar_hatasi: Gereksiz tekrarlama
   - ters_cevirme_hatasi: Harf/hece sirasi degisimi
   - nefes_hatasi: Yanlis yerde durma
   - vurgu_tonlama_hatasi: Yanlis vurgu, monoton okuma
   - hiz_hatasi: Cok yavas/hizli okuma

4. SADECE asagidaki JSON formatinda yanit ver, baska hicbir sey ekleme:

{{
  "transkripsiyon": "<ogrencinin okudugu metin>",
  "ozet": {{
    "toplam_kelime": {word_count},
    "dogru_okunan": 0,
    "toplam_hata": 0,
    "dogruluk_yuzdesi": 0,
    "okuma_hizi_wpm": {wpm if wpm else "null"},
    "genel_duzey": "Orta",
    "genel_duzey_emoji": "🟡"
  }},
  "hata_dagilimi": {{
    "harf_hatasi": 0, "hece_hatasi": 0, "kelime_hatasi": 0,
    "atlama_hatasi": 0, "ekleme_hatasi": 0, "tekrar_hatasi": 0,
    "ters_cevirme_hatasi": 0, "nefes_hatasi": 0,
    "vurgu_tonlama_hatasi": 0, "hiz_hatasi": 0
  }},
  "hata_detaylari": [
    {{"kategori": "harf_hatasi", "orijinal": "ornek", "okunan": "ornek2", "aciklama": "aciklama"}}
  ],
  "okuma_profili": {{
    "akicilik": "Kismen Akici",
    "prozodi": "Orta",
    "ozguven": "Orta",
    "dikkat": "Orta"
  }},
  "guclu_yonler": ["madde1", "madde2", "madde3"],
  "gelisim_alanlari": ["madde1", "madde2", "madde3"],
  "oneriler": {{
    "ogrenci_icin": ["oneri1", "oneri2", "oneri3", "oneri4", "oneri5"],
    "aile_icin": ["oneri1", "oneri2", "oneri3", "oneri4"],
    "ogretmen_icin": ["oneri1", "oneri2", "oneri3", "oneri4"]
  }},
  "egzersiz_plani": {{
    "gunluk": "gunluk plan",
    "haftalik": "haftalik plan",
    "hedef": "1 ay hedef"
  }},
  "uyari_notlari": [],
  "detayli_rapor": "# Markdown formatinda en az 1500 kelimelik rapor..."
}}

SADECE JSON dondur. {grade}. sinif beklentilerini goz onunde bulundur. Olumlu ve yapici ton kullan."""

    try:
        response = client.messages.create(
            model=get_claude_model(),
            max_tokens=16000,
            temperature=0.2,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": audio_b64,
                        },
                    },
                    {"type": "text", "text": prompt_text}
                ]
            }]
        )
        return response.content[0].text, None
    except Exception as e:
        return None, f"Claude API Hatasi: {str(e)}"


def call_claude_text(prompt, max_tokens=16000):
    """Metin tabanli Claude cagrisi (yedek yontem)."""
    client = get_claude_client()
    if not client:
        return None, "Claude API Key bulunamadi."
    try:
        response = client.messages.create(
            model=get_claude_model(), max_tokens=max_tokens, temperature=0.2,
            messages=[{"role": "user", "content": prompt}])
        return response.content[0].text, None
    except Exception as e:
        return None, str(e)


# ============================================================
# ANA APP
# ============================================================
def app():
    st.markdown("""
    <style>
        .main-header { text-align: center; font-weight: 900; font-size: 2.2rem; margin-bottom: 5px; color: #1B2A4A; }
        .sub-header { text-align: center; margin-bottom: 25px; font-size: 1rem; color: #555; }
        .test-card { background: #fff; border: 1px solid #E0E4EA; border-radius: 16px; padding: 24px 20px;
                     margin-bottom: 16px; text-align: center; transition: all 0.3s ease; }
        .test-card:hover { transform: translateY(-4px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
        .stat-box { background: #fff; border: 1px solid #E0E4EA; border-radius: 14px; padding: 20px; text-align: center; }
        .stat-number { font-size: 2rem; font-weight: 800; color: #1B2A4A; }
        .stat-label { font-size: 0.8rem; color: #999; margin-top: 4px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='main-header'>📖 OKUMA ANALİZ MERKEZİ</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-header'>Hosgeldin <b>{st.session_state.student_name}</b> — {st.session_state.student_grade}. Sinif</div>", unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = "home"

    ALL_TESTS = ["Okuma Hata Analizi", "Hizli Okuma Testi"]

    # ============================================================
    # ANA MENU
    # ============================================================
    if st.session_state.page == "home":
        completed_tests = get_completed_tests(st.session_state.student_id)

        sc1, sc2 = st.columns(2)
        with sc1:
            done = sum(1 for t in ALL_TESTS if t in completed_tests)
            st.markdown(f'<div class="stat-box"><div class="stat-number">{done}/{len(ALL_TESTS)}</div><div class="stat-label">Tamamlanan Test</div></div>', unsafe_allow_html=True)
        with sc2:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{st.session_state.student_grade}.</div><div class="stat-label">Sinif Duzeyi</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        test_metas = {
            "Okuma Hata Analizi": {"icon": "🎙️", "color": "#DC2626", "duration": "~5-10 dk",
                                    "desc": "Metni sesli oku, ses kaydini yukle, AI hata analizi yapsin."},
            "Hizli Okuma Testi": {"icon": "⏱️", "color": "#E67E22", "duration": "~5 dk",
                                   "desc": "Okuma hizini olc ve okudugunu ne kadar anladigini test et."},
        }

        col1, col2 = st.columns(2)
        for idx, test in enumerate(ALL_TESTS):
            is_done = test in completed_tests
            meta = test_metas[test]
            target_col = col1 if idx == 0 else col2

            with target_col:
                badge_txt = "✅ Tamamlandi" if is_done else "🎯 Hazir"
                badge_bg = "#d4edda;color:#155724" if is_done else "#d1ecf1;color:#0c5460"
                st.markdown(f"""
                    <div class="test-card" style="border-top: 4px solid {meta['color']};">
                        <div style="font-size: 2.5rem;">{meta['icon']}</div>
                        <div style="font-weight:700;font-size:1rem;color:#1B2A4A;margin:8px 0;">{test}</div>
                        <div style="font-size:0.82rem;color:#777;margin-bottom:10px;">{meta['desc']}</div>
                        <div style="font-size:0.75rem;color:#999;">⏱️ {meta['duration']}</div>
                        <span style="background:{badge_bg};padding:6px 14px;border-radius:20px;font-size:0.8rem;font-weight:700;display:inline-block;margin-top:8px;">{badge_txt}</span>
                    </div>
                """, unsafe_allow_html=True)

                if not is_done:
                    if st.button(f"▶️ {test} Basla", key=test, type="primary"):
                        st.session_state.selected_test = test
                        if test == "Okuma Hata Analizi":
                            metin = get_metin_for_grade(st.session_state.student_grade)
                            st.session_state.oha_metin = metin
                            st.session_state.oha_phase = "instructions"
                        elif test == "Hizli Okuma Testi":
                            grade = min(st.session_state.student_grade, 8)
                            passage, kademe = get_passage_for_grade(grade)
                            st.session_state.sr_passage = passage
                            st.session_state.sr_kademe = kademe
                            st.session_state.sr_phase = "reading"
                            st.session_state.sr_start_time = None
                            st.session_state.sr_reading_time = None
                            st.session_state.sr_answers = {}
                        st.session_state.page = "test"
                        st.rerun()

    # ============================================================
    # BASARI EKRANI
    # ============================================================
    elif st.session_state.page == "success_screen":
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1B2A4A, #2C3E6B); color: white;
                        border-radius: 16px; padding: 25px; text-align: center; margin: 20px 0;">
                <h3 style="color:#fff;">🎉 Harika Is Cikardin!</h3>
                <p>Testi basariyla tamamladin.</p>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.get("last_report"):
            with st.expander("📋 Raporunu Goruntule", expanded=True):
                st.markdown(st.session_state.last_report)

        st.markdown("---")
        c1, c2 = st.columns(2)
        if c1.button("🏠 Ana Menuye Don", type="primary"):
            st.session_state.page = "home"
            st.rerun()
        if c2.button("🚪 Cikis Yap"):
            st.session_state.clear()
            st.rerun()

    # ============================================================
    # TEST EKRANI
    # ============================================================
    elif st.session_state.page == "test":
        t_name = st.session_state.selected_test

        bar1, bar2 = st.columns([3, 1])
        with bar1:
            icon = "🎙️" if "Okuma" in t_name else "⏱️"
            st.markdown(f"### {icon} {t_name}")
        with bar2:
            if st.button("🏠 Ana Menu"):
                st.session_state.page = "home"
                st.rerun()

        st.markdown("---")

        # ========================================
        # OKUMA HATA ANALIZI
        # ========================================
        if t_name == "Okuma Hata Analizi":
            metin = st.session_state.oha_metin
            phase = st.session_state.oha_phase
            grade = st.session_state.student_grade

            # --- ADIM 1: YONERGE ---
            if phase == "instructions":
                st.markdown(f"""
                <div style="background: #FFF3E0; border: 1px solid #FFB74D; border-radius: 12px; padding: 20px;">
                    <div style="font-weight: 700; color: #E65100; font-size: 1.1rem; margin-bottom: 12px;">
                        📖 Okuma Hata Analizi
                    </div>
                    <div style="font-size: 0.95rem; color: #444; line-height: 1.8;">
                        <b>1.</b> Sana {grade}. sinif duzeyine uygun bir metin gosterilecek<br>
                        <b>2.</b> Ekrandaki 🎤 <b>mikrofon butonuna</b> bas ve metni sesli oku<br>
                        <b>3.</b> Okuma bitince mikrofon butonuna tekrar bas (kayit durur)<br>
                        <b>4.</b> <b>"AI Analizini Baslat"</b> butonuna bas<br>
                        <b>5.</b> Claude AI ses kaydini dinleyip hata raporu olusturacak
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("")
                st.markdown(f"""
                <div style="background: #E8F5E9; border: 1px solid #A5D6A7; border-radius: 12px; padding: 16px;">
                    📝 <b>Metin:</b> "{metin['title']}" — <b>{metin['kelime_sayisi']} kelime</b>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("")
                st.info("💡 Normalce oku — dogru ya da yanlis olmasinin onemi yok!")

                if st.button("HAZIRIM, BASLA! 🚀", type="primary", use_container_width=True):
                    st.session_state.oha_phase = "reading"
                    st.session_state.oha_start_time = time.time()
                    st.rerun()

            # --- ADIM 2: METIN + SES KAYDI ---
            elif phase == "reading":
                start_time = st.session_state.get("oha_start_time", time.time())
                elapsed = int(time.time() - start_time)

                # Zamanlayici
                components.html(f"""
                <div style="background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border: 1px solid #FFB74D;
                    border-radius: 12px; padding: 12px 20px; display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 1.5rem;">⏱️</span>
                    <div>
                        <div id="t1" style="font-weight:700;color:#E65100;font-size:1.2rem;font-family:monospace;">00:00</div>
                        <div style="font-size:0.8rem;color:#888;">Metni sesli oku — asagidan kayit al</div>
                    </div>
                </div>
                <script>
                (function(){{var el=document.getElementById('t1');var e={elapsed};
                function p(n){{return n<10?'0'+n:''+n;}}
                function u(){{el.textContent=p(Math.floor(e/60))+':'+p(e%60);}}
                u();setInterval(function(){{e++;u();}},1000);}})();
                </script>
                """, height=65)

                # METIN
                st.markdown(f"### 📖 {metin['title']}")
                for para in metin["text"].split("\n\n"):
                    if para.strip():
                        st.markdown(f"""
                        <div style="background:#fff;border:1px solid #E8E8E8;border-radius:10px;
                            padding:18px 22px;margin:8px 0;font-size:1.15rem;line-height:2.0;
                            color:#333;text-align:justify;">{para.strip()}</div>
                        """, unsafe_allow_html=True)

                st.markdown("---")

                # ========================================
                # 🎤 SES KAYDI — st.audio_input
                # ========================================
                st.markdown("""
                <div style="background: linear-gradient(135deg, #EDE7F6, #D1C4E9); border: 1px solid #B39DDB;
                    border-radius: 12px; padding: 20px; margin-bottom: 16px;">
                    <div style="font-weight: 700; color: #4527A0; font-size: 1.1rem; margin-bottom: 8px;">
                        🎤 Ses Kaydini Al
                    </div>
                    <div style="font-size: 0.9rem; color: #555; line-height: 1.6;">
                        Asagidaki <b>mikrofon ikonuna</b> tikla → metni sesli oku → bitince tekrar tikla.<br>
                        Kayit otomatik olarak yuklenecek.
                    </div>
                </div>
                """, unsafe_allow_html=True)

                audio_data = st.audio_input("🎤 Mikrofon butonuna bas ve metni sesli oku:", key="ses_kaydi")

                if audio_data is not None:
                    st.audio(audio_data)
                    st.success("✅ Ses kaydi alindi! Simdi analiz butonuna bas.")

                    if st.button("🤖 AI ANALİZİNİ BAŞLAT", type="primary", use_container_width=True):
                        reading_time = time.time() - st.session_state.oha_start_time

                        audio_bytes = audio_data.getvalue()
                        audio_name = getattr(audio_data, 'name', 'recording.wav')
                        audio_ext = audio_name.rsplit('.', 1)[-1].lower() if '.' in audio_name else 'wav'

                        progress_bar = st.progress(0, text="🎧 Ses kaydi Claude AI'a gonderiliyor...")
                        progress_bar.progress(20, text="🎧 Claude ses kaydini dinliyor...")

                        ai_response, err = analyze_audio_with_claude(
                            audio_bytes=audio_bytes,
                            audio_format=audio_ext,
                            original_text=metin["text"],
                            grade=grade,
                            student_name=st.session_state.get("student_name", ""),
                            student_age=st.session_state.get("student_age"),
                            reading_time_seconds=reading_time,
                        )

                        progress_bar.progress(80, text="📊 Analiz sonuclari isleniyor...")

                        if err:
                            progress_bar.empty()
                            st.error(f"❌ {err}")
                            st.warning("💡 Ses kaydi gonderilemedi. Asagidan yazili giris yapabilirsin.")
                            _show_text_input_fallback(metin, grade, reading_time)
                        else:
                            progress_bar.progress(100, text="✅ Analiz tamamlandi!")
                            time.sleep(0.5)
                            progress_bar.empty()
                            _process_ai_response(ai_response, metin, grade, reading_time)

                else:
                    st.markdown("")
                    with st.expander("📝 Ses kaydi yukleyemiyorsan — Yazili Giris", expanded=False):
                        reading_time = time.time() - st.session_state.oha_start_time
                        _show_text_input_fallback(metin, grade, reading_time)

            elif phase == "results":
                analysis = st.session_state.get("oha_analysis")
                if analysis:
                    report = generate_summary_report(analysis, grade,
                                                     st.session_state.get("oha_reading_time"))
                    st.session_state.last_report = report
                    st.session_state.page = "success_screen"
                    st.rerun()

        # ========================================
        # HIZLI OKUMA TESTI
        # ========================================
        elif t_name == "Hizli Okuma Testi":
            _render_speed_reading_test()


# ============================================================
# YARDIMCI FONKSIYONLAR
# ============================================================

def _show_text_input_fallback(metin, grade, reading_time):
    """Yazili giris yedek yontemi."""
    st.info("Ogrencinin okudugu metni tam olarak duydugu gibi yazin. Hatalari duzeltmeyin.")
    transcription = st.text_area("Okunan metin:", height=200,
        placeholder="Ogrencinin sesli okumasini buraya yazin...", key="oha_text_fb")
    if st.button("🤖 Yazili Giris ile Analiz Et", key="btn_text_az"):
        if not transcription or len(transcription.strip()) < 10:
            st.error("Lutfen metni girin.")
        else:
            with st.spinner("🤖 Claude AI analiz yapiyor..."):
                prompt = build_okuma_hata_prompt(
                    original_text=metin["text"], transcription=transcription.strip(),
                    grade=grade, student_name=st.session_state.get("student_name", ""),
                    student_age=st.session_state.get("student_age"),
                    reading_time_seconds=reading_time)
                ai_response, err = call_claude_text(prompt)
            if err:
                st.error(f"❌ {err}")
            else:
                _process_ai_response(ai_response, metin, grade, reading_time)


def _process_ai_response(ai_response, metin, grade, reading_time):
    """Claude yanitini parse edip kaydeder."""
    analysis, parse_err = parse_ai_response(ai_response)

    if parse_err:
        scores_db = {"raw_response": True}
        save_test_result_to_db(
            st.session_state.student_id, "Okuma Hata Analizi",
            {"original_text": metin["text"]}, scores_db, ai_response)
        st.session_state.last_report = ai_response
        st.session_state.page = "success_screen"
        st.rerun()
        return

    ozet = analysis.get("ozet", {})
    hata_dag = analysis.get("hata_dagilimi", {})

    scores_db = {
        "dogruluk_yuzdesi": ozet.get("dogruluk_yuzdesi", 0),
        "toplam_hata": ozet.get("toplam_hata", 0),
        "toplam_kelime": ozet.get("toplam_kelime", 0),
        "okuma_hizi_wpm": ozet.get("okuma_hizi_wpm"),
        "genel_duzey": ozet.get("genel_duzey", ""),
        "hata_dagilimi": hata_dag,
        "okuma_profili": analysis.get("okuma_profili", {}),
        "transkripsiyon": analysis.get("transkripsiyon", ""),
    }

    report = generate_summary_report(analysis, grade, reading_time)

    save_test_result_to_db(
        st.session_state.student_id, "Okuma Hata Analizi",
        {"original_text": metin["text"], "transkripsiyon": analysis.get("transkripsiyon", "")},
        scores_db, report)

    st.session_state.last_report = report
    st.session_state.page = "success_screen"
    st.rerun()


def _render_speed_reading_test():
    """Hizli okuma testi."""
    passage = st.session_state.sr_passage
    kademe = st.session_state.sr_kademe
    phase = st.session_state.sr_phase

    if phase == "reading":
        word_count = ho_count_words(passage["text"])
        if st.session_state.sr_start_time is None:
            st.session_state.sr_start_time = time.time()

        st.markdown(f"### 📖 {passage['title']}")
        st.caption(f"{word_count} kelime")

        elapsed = int(time.time() - st.session_state.sr_start_time)
        components.html(f"""
        <div style="background:linear-gradient(135deg,#FFF3E0,#FFE0B2);border:1px solid #FFB74D;
            border-radius:12px;padding:12px 20px;display:flex;align-items:center;gap:12px;">
            <span style="font-size:1.5rem;">⏱️</span>
            <div id="sr_c" style="font-weight:700;color:#E65100;font-size:1.1rem;font-family:monospace;">00:00</div>
        </div>
        <script>
        (function(){{var el=document.getElementById('sr_c');var e={elapsed};function p(n){{return n<10?'0'+n:''+n;}}
        function u(){{el.textContent=p(Math.floor(e/60))+':'+p(e%60);}}u();setInterval(function(){{e++;u();}},1000);}})();
        </script>
        """, height=55)

        for para in passage["text"].split("\n\n"):
            if para.strip():
                st.markdown(f"""<div style="background:#fff;border:1px solid #E8E8E8;border-radius:10px;
                    padding:18px 22px;margin:8px 0;font-size:1.05rem;line-height:1.8;color:#333;
                    text-align:justify;">{para.strip()}</div>""", unsafe_allow_html=True)

        if st.button("✅ Okudum, Sorulara Gec", type="primary", use_container_width=True):
            st.session_state.sr_reading_time = time.time() - st.session_state.sr_start_time
            st.session_state.sr_phase = "questions"
            st.rerun()

    elif phase == "questions":
        questions = passage["questions"]
        rt = st.session_state.sr_reading_time
        st.markdown("### 🧠 Okudugunu Anlama Sorulari")
        st.markdown(f"⏱️ Okuma suren: **{int(rt)//60} dk {int(rt)%60} sn**")
        st.warning("📌 Metin artik gorunmuyor.")

        with st.form("sr_q"):
            for i, q in enumerate(questions):
                prev = st.session_state.sr_answers.get(q["id"])
                keys = list(q["options"].keys())
                idx_prev = keys.index(prev) if prev in keys else None
                val = st.radio(f"**{i+1}. {q['text']}**", keys, index=idx_prev,
                               format_func=lambda k, o=q["options"]: f"{k}) {o[k]}",
                               key=f"sr_{q['id']}")
                if val:
                    st.session_state.sr_answers[q["id"]] = val
                st.divider()
            submitted = st.form_submit_button("Testi Bitir ✅", type="primary")

        if submitted:
            answered = sum(1 for q in questions if q["id"] in st.session_state.sr_answers)
            if answered < len(questions):
                st.error(f"⚠️ {len(questions)-answered} soru bos.")
            else:
                with st.spinner("📊 Hesaplaniyor..."):
                    scores = calculate_speed_reading(st.session_state.sr_answers, passage, rt, kademe)
                    report = generate_speed_reading_report(scores)
                    scores_db = {"wpm": scores["wpm"], "speed_label": scores["speed_label"],
                                 "comprehension_pct": scores["comprehension_pct"],
                                 "effective_score": scores["effective_score"], "profile": scores["profile"]}
                    save_test_result_to_db(st.session_state.student_id, "Hizli Okuma Testi",
                                           st.session_state.sr_answers, scores_db, report)
                    st.session_state.last_report = report
                    st.session_state.page = "success_screen"
                    st.rerun()

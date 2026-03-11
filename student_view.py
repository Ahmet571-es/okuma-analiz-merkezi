# ============================================================
# student_view.py — Öğrenci Test Arayüzü
# Okuma Hata Analizi + Hızlı Okuma Testi
# ============================================================

import streamlit as st
import streamlit.components.v1 as components
import time
import json
import base64
import os
import io
import tempfile
from datetime import datetime
from db_utils import save_test_result_to_db, get_completed_tests
from okuma_hata_engine import (
    OKUMA_METINLERI, HATA_KATEGORILERI, OKUMA_HIZI_NORMLARI,
    get_metin_for_grade, count_words, classify_reading_speed,
    build_okuma_hata_prompt, parse_ai_response, calculate_overall_score,
    get_performance_level, generate_summary_report,
)
from hizli_okuma_engine import (
    get_passage_for_grade, count_words as ho_count_words,
    calculate_speed_reading, generate_speed_reading_report,
    KADEME_LABELS, WPM_NORMS,
)

# ============================================================
# AI CLIENT
# ============================================================
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

def get_claude_model():
    try:
        if "CLAUDE_MODEL" in st.secrets: return st.secrets["CLAUDE_MODEL"]
    except: pass
    return os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")

def call_claude(prompt, max_tokens=16000):
    client = get_claude_client()
    if not client:
        return None, "Claude API Key bulunamadı."
    try:
        response = client.messages.create(
            model=get_claude_model(),
            max_tokens=max_tokens,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text, None
    except Exception as e:
        return None, str(e)


def transcribe_audio_with_claude(audio_bytes, original_text, grade):
    """Claude API ile ses kaydını transkribe eder."""
    client = get_claude_client()
    if not client:
        return None, "Claude API Key bulunamadı."
    try:
        audio_b64 = base64.standard_b64encode(audio_bytes).decode("utf-8")

        prompt_text = f"""Aşağıdaki ses kaydı, {grade}. sınıf düzeyinde bir Türk öğrencinin sesli okumasıdır.

Öğrencinin okuması gereken orijinal metin:
```
{original_text}
```

Lütfen ses kaydını DİKKATLİCE dinle ve öğrencinin GERÇEKTE ne söylediğini olduğu gibi transkribe et.

ÖNEMLİ KURALLAR:
1. Öğrencinin söylediğini AYNEN yaz — düzeltme yapma
2. Yanlış okunan kelimeleri yanlış haliyle yaz
3. Atlanan kelimeleri yazma
4. Eklenen kelimeleri yaz
5. Tekrarlanan kelimeleri tekrar yaz
6. Duraksamaları [...] ile göster

SADECE transkripsiyon metnini döndür."""

        response = client.messages.create(
            model=get_claude_model(),
            max_tokens=4000,
            temperature=0.1,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "audio/wav",
                            "data": audio_b64,
                        },
                    },
                    {"type": "text", "text": prompt_text}
                ]
            }]
        )
        return response.content[0].text.strip(), None
    except Exception as e:
        err = str(e)
        if "Could not process" in err or "audio" in err.lower():
            return None, "audio_not_supported"
        return None, f"Transkripsiyon hatası: {err}"


# ============================================================
# SES KAYDI HTML COMPONENT
# ============================================================
def render_audio_recorder():
    """Tarayıcı tabanlı ses kaydedici — WAV formatında."""
    recorder_html = """
    <div id="recorder-container" style="text-align:center; padding: 20px; background: #f8fafc; border-radius: 16px; border: 2px dashed #cbd5e1;">
        <div id="status" style="font-size: 1.2rem; font-weight: 700; color: #1e293b; margin-bottom: 15px;">
            🎙️ Kayda Hazır
        </div>
        <div id="timer" style="font-size: 2.5rem; font-weight: 800; color: #2563eb; font-family: monospace; margin: 10px 0;">
            00:00
        </div>
        <div style="margin: 15px 0;">
            <button id="startBtn" onclick="startRecording()" style="background: linear-gradient(135deg, #10b981, #059669); color: white; border: none; padding: 14px 36px; border-radius: 12px; font-size: 1.1rem; font-weight: 700; cursor: pointer; margin: 5px;">
                ▶️ KAYDI BAŞLAT
            </button>
            <button id="stopBtn" onclick="stopRecording()" disabled style="background: linear-gradient(135deg, #ef4444, #dc2626); color: white; border: none; padding: 14px 36px; border-radius: 12px; font-size: 1.1rem; font-weight: 700; cursor: pointer; margin: 5px; opacity: 0.5;">
                ⏹️ KAYDI BİTİR
            </button>
        </div>
        <audio id="audioPlayback" controls style="display:none; margin-top: 15px; width: 100%;"></audio>
        <div id="download-area" style="display:none; margin-top: 10px;">
            <p style="color: #10b981; font-weight: 600;">✅ Kayıt tamamlandı!</p>
        </div>
    </div>

    <script>
    let mediaRecorder;
    let audioChunks = [];
    let timerInterval;
    let seconds = 0;
    let audioBlob = null;

    function updateTimer() {
        seconds++;
        const m = Math.floor(seconds / 60).toString().padStart(2, '0');
        const s = (seconds % 60).toString().padStart(2, '0');
        document.getElementById('timer').textContent = m + ':' + s;
    }

    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
            audioChunks = [];
            seconds = 0;

            mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) audioChunks.push(e.data); };
            mediaRecorder.onstop = () => {
                audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const url = URL.createObjectURL(audioBlob);
                const audio = document.getElementById('audioPlayback');
                audio.src = url;
                audio.style.display = 'block';
                document.getElementById('download-area').style.display = 'block';
                document.getElementById('status').innerHTML = '✅ Kayıt Tamamlandı — Dinleyebilirsin';
                document.getElementById('status').style.color = '#10b981';

                // Convert to base64 and send to Streamlit
                const reader = new FileReader();
                reader.onloadend = () => {
                    const base64data = reader.result.split(',')[1];
                    // Send to Streamlit via session state
                    window.parent.postMessage({
                        type: 'audio_data',
                        data: base64data,
                        duration: seconds
                    }, '*');
                };
                reader.readAsDataURL(audioBlob);

                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start(100);
            timerInterval = setInterval(updateTimer, 1000);

            document.getElementById('startBtn').disabled = true;
            document.getElementById('startBtn').style.opacity = '0.5';
            document.getElementById('stopBtn').disabled = false;
            document.getElementById('stopBtn').style.opacity = '1';
            document.getElementById('status').innerHTML = '🔴 KAYIT YAPILIYOR...';
            document.getElementById('status').style.color = '#ef4444';
        } catch(err) {
            document.getElementById('status').innerHTML = '❌ Mikrofon izni gerekli!';
            document.getElementById('status').style.color = '#ef4444';
        }
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            clearInterval(timerInterval);
            document.getElementById('startBtn').disabled = false;
            document.getElementById('startBtn').style.opacity = '1';
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('stopBtn').style.opacity = '0.5';
        }
    }
    </script>
    """
    return recorder_html


# ============================================================
# ANA APP FONKSİYONU
# ============================================================
def app():
    st.markdown("""
    <style>
        .main-header { text-align: center; font-weight: 900; font-size: 2.2rem; margin-bottom: 5px; color: #1B2A4A; }
        .sub-header { text-align: center; margin-bottom: 25px; font-size: 1rem; color: #555; }
        .test-card { background: #fff; border: 1px solid #E0E4EA; border-radius: 16px; padding: 24px 20px; margin-bottom: 16px; text-align: center; transition: all 0.3s ease; position: relative; overflow: hidden; }
        .test-card::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 4px; }
        .test-card:hover { transform: translateY(-4px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
        .stat-box { background: #fff; border: 1px solid #E0E4EA; border-radius: 14px; padding: 20px; text-align: center; }
        .stat-number { font-size: 2rem; font-weight: 800; color: #1B2A4A; }
        .stat-label { font-size: 0.8rem; color: #999; margin-top: 4px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='main-header'>📖 OKUMA ANALİZ MERKEZİ</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-header'>Hoşgeldin <b>{st.session_state.student_name}</b> — Sınıf: {st.session_state.student_grade}. Sınıf</div>", unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = "home"

    ALL_TESTS = ["Okuma Hata Analizi", "Hızlı Okuma Testi"]

    # ============================================================
    # ANA MENÜ
    # ============================================================
    if st.session_state.page == "home":
        completed_tests = get_completed_tests(st.session_state.student_id)

        sc1, sc2 = st.columns(2)
        with sc1:
            completed_count = sum(1 for t in ALL_TESTS if t in completed_tests)
            st.markdown(f'<div class="stat-box"><div class="stat-number">{completed_count}/{len(ALL_TESTS)}</div><div class="stat-label">Tamamlanan Test</div></div>', unsafe_allow_html=True)
        with sc2:
            grade = st.session_state.student_grade
            st.markdown(f'<div class="stat-box"><div class="stat-number">{grade}.</div><div class="stat-label">Sınıf Düzeyi</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        # TEST KARTLARI
        test_metas = {
            "Okuma Hata Analizi": {"icon": "🎙️", "color": "#DC2626", "duration": "~5-10 dk", "desc": "Metni sesli oku, AI hata analizi yapsın. Harf, hece, kelime, atlama, nefes hatalarını tespit et."},
            "Hızlı Okuma Testi": {"icon": "⏱️", "color": "#E67E22", "duration": "~5 dk", "desc": "Okuma hızını ölç ve okuduğunu ne kadar anladığını test et."},
        }

        col1, col2 = st.columns(2)
        for idx, test in enumerate(ALL_TESTS):
            is_done = test in completed_tests
            meta = test_metas[test]
            target_col = col1 if idx == 0 else col2

            with target_col:
                badge = '<span style="background:#d4edda;color:#155724;padding:6px 14px;border-radius:20px;font-size:0.8rem;font-weight:700;">✅ Tamamlandı</span>' if is_done else '<span style="background:#d1ecf1;color:#0c5460;padding:6px 14px;border-radius:20px;font-size:0.8rem;font-weight:700;">🎯 Hazır</span>'
                st.markdown(f"""
                    <div class="test-card" style="--card-color: {meta['color']}; border-top: 4px solid {meta['color']};">
                        <div style="font-size: 2.5rem;">{meta['icon']}</div>
                        <div style="font-weight:700;font-size:1rem;color:#1B2A4A;margin:8px 0;">{test}</div>
                        <div style="font-size:0.82rem;color:#777;margin-bottom:10px;">{meta['desc']}</div>
                        <div style="font-size:0.75rem;color:#999;">⏱️ {meta['duration']}</div>
                        {badge}
                    </div>
                """, unsafe_allow_html=True)

                if not is_done:
                    if st.button(f"▶️ {test} Başla", key=test, type="primary"):
                        if test == "Okuma Hata Analizi":
                            metin = get_metin_for_grade(st.session_state.student_grade)
                            st.session_state.oha_metin = metin
                            st.session_state.oha_phase = "instructions"
                            st.session_state.oha_audio_data = None
                            st.session_state.oha_audio_duration = None
                            st.session_state.oha_transcription = None
                            st.session_state.oha_analysis = None
                        elif test == "Hızlı Okuma Testi":
                            grade = st.session_state.student_grade
                            if grade > 8: grade = 8
                            passage_data, kademe = get_passage_for_grade(grade)
                            st.session_state.sr_passage = passage_data
                            st.session_state.sr_kademe = kademe
                            st.session_state.sr_phase = "reading"
                            st.session_state.sr_start_time = None
                            st.session_state.sr_reading_time = None
                            st.session_state.sr_answers = {}

                        st.session_state.selected_test = test
                        st.session_state.page = "test"
                        st.rerun()

    # ============================================================
    # BAŞARI EKRANI
    # ============================================================
    elif st.session_state.page == "success_screen":
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1B2A4A, #2C3E6B); color: white; border-radius: 16px; padding: 25px; text-align: center; margin: 20px 0;">
                <h3 style="color: #fff;">🎉 Harika İş Çıkardın!</h3>
                <p>Testi başarıyla tamamladın. Sonuçların öğretmenine iletildi.</p>
            </div>
        """, unsafe_allow_html=True)

        if "last_report" in st.session_state and st.session_state.last_report:
            with st.expander("📋 Raporunu Görüntüle", expanded=True):
                st.markdown(st.session_state.last_report)

        st.markdown("---")
        c1, c2 = st.columns(2)
        if c1.button("🏠 Ana Menüye Dön", type="primary"):
            st.session_state.page = "home"
            st.rerun()
        if c2.button("🚪 Çıkış Yap"):
            st.session_state.clear()
            st.rerun()

    # ============================================================
    # TEST EKRANI
    # ============================================================
    elif st.session_state.page == "test":
        t_name = st.session_state.selected_test

        bar1, bar2 = st.columns([3, 1])
        with bar1:
            st.markdown(f"### {'🎙️' if 'Okuma' in t_name else '⏱️'} {t_name}")
        with bar2:
            if st.button("🏠 Ana Menü"):
                st.session_state.page = "home"
                st.rerun()

        st.markdown("---")

        # ========================================
        # OKUMA HATA ANALİZİ TESTİ
        # ========================================
        if t_name == "Okuma Hata Analizi":
            metin = st.session_state.oha_metin
            phase = st.session_state.oha_phase
            grade = st.session_state.student_grade

            # --- YÖNERGE ---
            if phase == "instructions":
                st.markdown(f"""
                    <div style="background: #FFF3E0; border: 1px solid #FFB74D; border-radius: 12px; padding: 20px; margin: 10px 0;">
                        <div style="font-weight: 700; color: #E65100; font-size: 1.05rem; margin-bottom: 12px;">📖 Okuma Hata Analizi Nasıl Çalışır?</div>
                        <div style="font-size: 0.92rem; color: #444; line-height: 1.7;">
                            <b>1.</b> Sana {grade}. sınıf düzeyine uygun bir metin gösterilecek<br>
                            <b>2.</b> Metni sesli olarak dikkatlice oku<br>
                            <b>3.</b> Okurken <b>ses kaydı</b> alınacak VEYA okuduğunu yazılı olarak gireceksin<br>
                            <b>4.</b> Yapay zekâ okumanı analiz edecek ve hata raporu oluşturacak<br>
                            <b>5.</b> Harf, hece, kelime, atlama, nefes hataları kategorize edilecek
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                    <div style="background: #E8F5E9; border: 1px solid #A5D6A7; border-radius: 12px; padding: 16px; margin: 10px 0;">
                        <b>📝 Metin Bilgisi:</b> "{metin['title']}" — {metin['kelime_sayisi']} kelime
                    </div>
                """, unsafe_allow_html=True)

                st.info("💡 Doğru ya da yanlış okumanın önemli değil — normalce oku, AI analiz edecek!")

                if st.button("HAZIRIM, BAŞLA! 🚀", type="primary", use_container_width=True):
                    st.session_state.oha_phase = "reading"
                    st.session_state.oha_start_time = time.time()
                    st.rerun()

            # --- OKUMA + KAYIT ---
            elif phase == "reading":
                st.markdown(f"### 📖 {metin['title']}")
                st.caption(f"{grade}. Sınıf — {metin['kelime_sayisi']} kelime")

                # Zamanlayıcı
                start_time = st.session_state.get("oha_start_time", time.time())
                elapsed = int(time.time() - start_time)
                components.html(f"""
                <div style="background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border: 1px solid #FFB74D;
                    border-radius: 12px; padding: 12px 20px; display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 1.5rem;">⏱️</span>
                    <div>
                        <div id="oha_timer" style="font-weight: 700; color: #E65100; font-size: 1.1rem; font-family: monospace;">00:00</div>
                        <div style="font-size: 0.8rem; color: #888;">Metni sesli oku</div>
                    </div>
                </div>
                <script>
                (function(){{
                    var el = document.getElementById('oha_timer');
                    var elapsed = {elapsed};
                    function pad(n){{ return n<10?'0'+n:''+n; }}
                    function update(){{ var m=Math.floor(elapsed/60); var s=elapsed%60; el.textContent=pad(m)+':'+pad(s); }}
                    update();
                    setInterval(function(){{ elapsed++; update(); }}, 1000);
                }})();
                </script>
                """, height=65)

                # Metin gösterimi
                paragraphs = metin["text"].split("\n\n")
                for para in paragraphs:
                    if para.strip():
                        st.markdown(f"""
                            <div style="background: #fff; border: 1px solid #E8E8E8; border-radius: 10px;
                                padding: 18px 22px; margin: 8px 0; font-size: 1.15rem;
                                line-height: 2.0; color: #333; text-align: justify;">
                                {para.strip()}
                            </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")

                # OKUMA TAMAMLANDI BUTONU
                if st.button("✅ OKUMAM BİTTİ — Devam Et", type="primary", use_container_width=True):
                    reading_time = time.time() - st.session_state.oha_start_time
                    st.session_state.oha_reading_time = reading_time
                    st.session_state.oha_phase = "input"
                    st.rerun()

            # --- TRANSKRIPT GİRİŞ ---
            elif phase == "input":
                reading_time = st.session_state.get("oha_reading_time", 0)
                mins = int(reading_time) // 60
                secs = int(reading_time) % 60

                st.markdown(f"""
                    <div style="background: #E8F5E9; border: 1px solid #A5D6A7; border-radius: 12px; padding: 12px 20px;">
                        <span style="font-weight: 600; color: #2E7D32;">⏱️ Okuma süren: {mins} dk {secs} sn</span>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("### 📝 Okuduğun Metni Gir")
                st.info("💡 **Yöntem:** Aşağıdaki kutucuğa, öğrencinin okuduğu metni **tam olarak duyulduğu gibi** yazın. Hataları düzeltmeden, olduğu gibi aktarın. Öğretmen veya veli bu adımı yapabilir.")

                # SES KAYDI SEÇENEĞİ (Eğer Claude ses destekliyorsa)
                input_method = st.radio(
                    "Giriş Yöntemi:",
                    ["📝 Yazılı Giriş (Transkript)", "🎙️ Ses Kaydı Yükle"],
                    index=0,
                    horizontal=True
                )

                if input_method == "📝 Yazılı Giriş (Transkript)":
                    transcription = st.text_area(
                        "Öğrencinin okuduğu metin (tam olarak duyulduğu gibi):",
                        height=250,
                        placeholder="Öğrencinin sesli okumasını buraya yazın. Yanlış okunan kelimeleri yanlış haliyle, atlanan kelimeleri atlanmış olarak, eklenen kelimeleri eklenmiş haliyle yazın...",
                        key="oha_transcript_input"
                    )

                    if st.button("🤖 AI ANALİZİ BAŞLAT", type="primary", use_container_width=True):
                        if not transcription or len(transcription.strip()) < 10:
                            st.error("⚠️ Lütfen öğrencinin okuduğu metni girin.")
                        else:
                            _run_analysis(metin, transcription.strip(), grade, reading_time)

                else:  # Ses Kaydı Yükle
                    st.markdown("""
                        <div style="background: #EDE7F6; border: 1px solid #B39DDB; border-radius: 12px; padding: 16px; margin: 10px 0;">
                            <b>🎙️ Ses Kaydı Yükleme:</b> Öğrencinin sesli okumasını WAV, MP3 veya M4A formatında yükleyin.
                            Ses kaydı Claude AI tarafından transkribe edilecek ve analiz edilecektir.
                        </div>
                    """, unsafe_allow_html=True)

                    uploaded_audio = st.file_uploader(
                        "Ses dosyası seç (WAV, MP3, M4A, WebM, OGG):",
                        type=["wav", "mp3", "m4a", "webm", "ogg"],
                        key="audio_upload"
                    )

                    if uploaded_audio:
                        st.audio(uploaded_audio, format=f"audio/{uploaded_audio.name.split('.')[-1]}")

                        if st.button("🤖 SES KAYDI İLE ANALİZ BAŞLAT", type="primary", use_container_width=True):
                            audio_bytes = uploaded_audio.read()

                            with st.spinner("🎧 Ses kaydı transkribe ediliyor..."):
                                transcription, err = transcribe_audio_with_claude(
                                    audio_bytes, metin["text"], grade
                                )

                            if err == "audio_not_supported":
                                st.warning("⚠️ Claude API ses dosyasını işleyemedi. Lütfen yazılı giriş yöntemini kullanın.")
                            elif err:
                                st.error(f"❌ Transkripsiyon hatası: {err}")
                            elif transcription:
                                st.success("✅ Transkripsiyon tamamlandı!")
                                with st.expander("📝 Transkripsiyon Sonucu", expanded=True):
                                    st.write(transcription)

                                _run_analysis(metin, transcription, grade, reading_time)

            # --- ANALİZ SONUÇLARI ---
            elif phase == "results":
                analysis = st.session_state.oha_analysis
                if analysis:
                    report = generate_summary_report(analysis, grade, st.session_state.get("oha_reading_time"))
                    st.session_state.last_report = report
                    st.session_state.page = "success_screen"
                    st.rerun()

        # ========================================
        # HIZLI OKUMA TESTİ
        # ========================================
        elif t_name == "Hızlı Okuma Testi":
            passage = st.session_state.sr_passage
            kademe = st.session_state.sr_kademe
            phase = st.session_state.sr_phase

            if phase == "reading":
                word_count = ho_count_words(passage["text"])
                if st.session_state.sr_start_time is None:
                    st.session_state.sr_start_time = time.time()

                st.markdown(f"### 📖 {passage['title']}")
                st.caption(f"{word_count} kelime")

                elapsed = time.time() - st.session_state.sr_start_time
                start_secs = int(elapsed)
                components.html(f"""
                <div style="background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border: 1px solid #FFB74D;
                    border-radius: 12px; padding: 12px 20px; display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 1.5rem;">⏱️</span>
                    <div id="sr_clock" style="font-weight: 700; color: #E65100; font-size: 1.1rem; font-family: monospace;">00:00</div>
                </div>
                <script>
                (function(){{
                    var el=document.getElementById('sr_clock'); var elapsed={start_secs};
                    function pad(n){{return n<10?'0'+n:''+n;}}
                    function up(){{var m=Math.floor(elapsed/60);var s=elapsed%60;el.textContent=pad(m)+':'+pad(s);}}
                    up(); setInterval(function(){{elapsed++;up();}},1000);
                }})();
                </script>
                """, height=55)

                for para in passage["text"].split("\n\n"):
                    if para.strip():
                        st.markdown(f"""
                            <div style="background: #fff; border: 1px solid #E8E8E8; border-radius: 10px;
                                padding: 18px 22px; margin: 8px 0; font-size: 1.05rem;
                                line-height: 1.8; color: #333; text-align: justify;">{para.strip()}</div>
                        """, unsafe_allow_html=True)

                if st.button("✅ Okudum, Sorulara Geç", type="primary", use_container_width=True):
                    st.session_state.sr_reading_time = time.time() - st.session_state.sr_start_time
                    st.session_state.sr_phase = "questions"
                    st.rerun()

            elif phase == "questions":
                questions = passage["questions"]
                reading_time = st.session_state.sr_reading_time
                mins = int(reading_time) // 60
                secs = int(reading_time) % 60

                st.markdown("### 🧠 Okuduğunu Anlama Soruları")
                st.markdown(f"⏱️ Okuma süren: **{mins} dk {secs} sn**")
                st.warning("📌 Metin artık görünmüyor. Hatırladıklarına göre cevapla.")

                with st.form("sr_questions"):
                    for i, q in enumerate(questions):
                        prev = st.session_state.sr_answers.get(q["id"])
                        keys = list(q["options"].keys())
                        idx_prev = keys.index(prev) if prev in keys else None
                        val = st.radio(
                            f"**{i+1}. {q['text']}**", keys,
                            index=idx_prev,
                            format_func=lambda k, o=q["options"]: f"{k}) {o[k]}",
                            key=f"sr_{q['id']}")
                        if val:
                            st.session_state.sr_answers[q["id"]] = val
                        st.divider()
                    submitted = st.form_submit_button("Testi Bitir ✅", type="primary")

                if submitted:
                    answered = sum(1 for q in questions if q["id"] in st.session_state.sr_answers)
                    if answered < len(questions):
                        st.error(f"⚠️ {len(questions) - answered} soru boş kaldı.")
                    else:
                        with st.spinner("📊 Hesaplanıyor..."):
                            scores = calculate_speed_reading(
                                st.session_state.sr_answers, passage,
                                st.session_state.sr_reading_time, kademe)
                            report = generate_speed_reading_report(scores)
                            scores_db = {
                                "wpm": scores["wpm"], "speed_label": scores["speed_label"],
                                "comprehension_pct": scores["comprehension_pct"],
                                "effective_score": scores["effective_score"],
                                "profile": scores["profile"],
                            }
                            save_test_result_to_db(
                                st.session_state.student_id, "Hızlı Okuma Testi",
                                st.session_state.sr_answers, scores_db, report)
                            st.session_state.last_report = report
                            st.session_state.page = "success_screen"
                            st.rerun()


def _run_analysis(metin, transcription, grade, reading_time):
    """Okuma hata analizini çalıştırır."""
    with st.spinner("🤖 Claude AI analiz yapıyor... Bu birkaç dakika sürebilir."):
        prompt = build_okuma_hata_prompt(
            original_text=metin["text"],
            transcription=transcription,
            grade=grade,
            student_name=st.session_state.get("student_name", ""),
            student_age=st.session_state.get("student_age"),
            reading_time_seconds=reading_time,
        )

        ai_response, err = call_claude(prompt, max_tokens=16000)

        if err:
            st.error(f"❌ AI Analiz Hatası: {err}")
            return

        analysis, parse_err = parse_ai_response(ai_response)

        if parse_err:
            st.warning(f"⚠️ JSON parse hatası. Ham rapor gösteriliyor.")
            # Ham yanıtı rapor olarak kaydet
            scores_db = {"transcription": transcription, "raw_ai_response": True}
            save_test_result_to_db(
                st.session_state.student_id, "Okuma Hata Analizi",
                {"transcription": transcription}, scores_db, ai_response)
            st.session_state.last_report = ai_response
            st.session_state.page = "success_screen"
            st.rerun()
            return

        # Başarılı analiz
        st.session_state.oha_analysis = analysis

        # Skorları kaydet
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
        }

        report = generate_summary_report(analysis, grade, reading_time)

        save_test_result_to_db(
            st.session_state.student_id, "Okuma Hata Analizi",
            {"transcription": transcription, "original_text": metin["text"]},
            scores_db, report)

        st.session_state.last_report = report
        st.session_state.page = "success_screen"
        st.rerun()

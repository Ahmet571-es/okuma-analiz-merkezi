"""
Öğrenci Arayüzü
— Ses kaydı alma + Hızlı okuma testi
"""

import streamlit as st
import base64
import time
from db_utils import save_audio_recording, get_recordings_by_user, save_speed_reading_result, get_speed_reading_results
from okuma_hata_engine import get_text_for_grade, HATA_KATEGORILERI
from hizli_okuma_engine import get_speed_reading_data, calculate_speed_reading_score


def render_student_view():
    """Öğrenci ana sayfasını render eder."""
    user = st.session_state.get("user")
    if not user:
        st.error("Oturum bulunamadı.")
        return
    
    # Üst bilgi
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1.5rem 2rem; border-radius: 16px; margin-bottom: 2rem; color: white;">
        <h2 style="margin:0; color:white;">👋 Merhaba, {user['name']}!</h2>
        <p style="margin:0.5rem 0 0 0; opacity:0.9;">{user['grade']}. Sınıf • Okuma Analiz Merkezi</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Ana menü
    tab1, tab2, tab3 = st.tabs(["🎤 Okuma Hata Analizi", "⚡ Hızlı Okuma Testi", "📊 Geçmiş Kayıtlarım"])
    
    with tab1:
        render_okuma_kaydi(user)
    
    with tab2:
        render_hizli_okuma(user)
    
    with tab3:
        render_gecmis_kayitlar(user)


def render_okuma_kaydi(user):
    """Sesli okuma kaydı arayüzü."""
    grade = user['grade']
    text_data = get_text_for_grade(grade)
    
    st.markdown("### 📖 Sesli Okuma Kaydı")
    st.markdown("""
    <div style="background: #EEF2FF; border-left: 4px solid #6366F1; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <strong>📌 Nasıl Yapılır?</strong><br>
        1. Aşağıdaki metni dikkatlice oku<br>
        2. Hazır olduğunda mikrofon butonuna bas ve metni sesli oku<br>
        3. Bitirince kaydı durdur ve "Kaydı Gönder" butonuna bas<br>
        4. Öğretmenin ses kaydını dinleyerek analiz yapacak
    </div>
    """, unsafe_allow_html=True)
    
    # Metin gösterimi
    st.markdown(f"""
    <div style="background: white; border: 2px solid #E2E8F0; border-radius: 12px; padding: 1.5rem; 
                margin: 1rem 0; font-size: 1.15rem; line-height: 1.9; color: #1E293B;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 1rem;">
            <span style="font-weight: 700; color: #6366F1;">📄 {text_data['baslik']}</span>
            <span style="background: #6366F1; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.85rem;">
                {text_data['kelime_sayisi']} kelime • {grade}. Sınıf
            </span>
        </div>
        <hr style="border: 1px solid #E2E8F0; margin-bottom: 1rem;">
        {text_data['metin']}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎤 Ses Kaydı")
    
    # Streamlit native audio input
    audio_data = st.audio_input(
        "Mikrofon butonuna basarak okumaya başla",
        key="student_audio_recorder"
    )
    
    if audio_data is not None:
        st.success("✅ Ses kaydı alındı! Aşağıdan dinleyebilirsin.")
        st.audio(audio_data, format="audio/wav")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Kaydı Gönder", type="primary", use_container_width=True):
                with st.spinner("Kayıt gönderiliyor..."):
                    # Base64'e çevir
                    audio_bytes = audio_data.getvalue()
                    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                    
                    success = save_audio_recording(
                        user_id=user['id'],
                        audio_base64=audio_b64,
                        text_id=text_data['id'],
                        original_text=text_data['metin'],
                    )
                    
                    if success:
                        st.balloons()
                        st.success("🎉 Ses kaydın başarıyla kaydedildi! Öğretmenin analiz edecek.")
                        st.info("💡 Öğretmenin ses kaydını dinleyerek detaylı bir okuma analizi yapacak. Sonuçları öğretmeninden öğrenebilirsin.")
                    else:
                        st.error("❌ Kayıt sırasında bir hata oluştu. Lütfen tekrar dene.")
        with col2:
            if st.button("🔄 Yeniden Kaydet", use_container_width=True):
                st.rerun()
    else:
        st.info("👆 Yukarıdaki mikrofon butonuna basarak okumaya başla.")


def render_hizli_okuma(user):
    """Hızlı okuma testi arayüzü."""
    grade = user['grade']
    data = get_speed_reading_data(grade)
    
    st.markdown("### ⚡ Hızlı Okuma Testi")
    st.markdown("""
    <div style="background: #FFF7ED; border-left: 4px solid #F59E0B; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <strong>📌 Nasıl Yapılır?</strong><br>
        1. "Testi Başlat" butonuna bas — metin görünecek<br>
        2. Metni <strong>sessizce</strong> ve hızlıca oku<br>
        3. Bitirince "Okumayı Bitirdim" butonuna bas<br>
        4. 10 anlama sorusunu cevapla<br>
        5. Sonuçlarını gör!
    </div>
    """, unsafe_allow_html=True)
    
    # Test durumları
    if "hizli_okuma_state" not in st.session_state:
        st.session_state.hizli_okuma_state = "ready"  # ready, reading, questions, results
    
    state = st.session_state.hizli_okuma_state
    
    if state == "ready":
        st.markdown(f"""
        <div style="background: white; border: 2px solid #E2E8F0; border-radius: 12px; padding: 1.5rem; text-align: center;">
            <h3 style="color: #6366F1;">📖 {data['baslik']}</h3>
            <p style="color: #64748B;">{grade}. Sınıf Düzeyi • {len(data['metin'].split())} kelime</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Testi Başlat", type="primary", use_container_width=True):
            st.session_state.hizli_okuma_state = "reading"
            st.session_state.hizli_okuma_start = time.time()
            st.rerun()
    
    elif state == "reading":
        # Zamanlayıcı başlamış, metin göster
        st.markdown(f"""
        <div style="background: white; border: 2px solid #6366F1; border-radius: 12px; padding: 2rem; 
                    font-size: 1.15rem; line-height: 1.9; color: #1E293B;">
            <div style="text-align: center; margin-bottom: 1rem;">
                <span style="background: #EF4444; color: white; padding: 0.3rem 1rem; border-radius: 20px; font-weight: 700;">
                    ⏱️ Zamanlayıcı çalışıyor...
                </span>
            </div>
            <hr style="border: 1px solid #E2E8F0; margin-bottom: 1rem;">
            {data['metin']}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ Okumayı Bitirdim!", type="primary", use_container_width=True):
            st.session_state.hizli_okuma_end = time.time()
            st.session_state.hizli_okuma_duration = st.session_state.hizli_okuma_end - st.session_state.hizli_okuma_start
            st.session_state.hizli_okuma_state = "questions"
            st.rerun()
    
    elif state == "questions":
        duration = st.session_state.hizli_okuma_duration
        word_count = len(data['metin'].split())
        wpm = (word_count / duration) * 60
        
        st.markdown(f"""
        <div style="background: #ECFDF5; border-radius: 12px; padding: 1rem; text-align: center; margin-bottom: 1rem;">
            <span style="font-size: 1.2rem; font-weight: 700; color: #059669;">
                ⏱️ Okuma süren: {duration:.1f} saniye • 📊 {wpm:.0f} kelime/dakika
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📝 Anlama Soruları")
        st.markdown("Metni hatırladığın kadarıyla soruları cevapla:")
        
        answers = {}
        for i, q in enumerate(data['sorular']):
            answers[i] = st.radio(
                f"**{i+1}.** {q['soru']}",
                q['secenekler'],
                key=f"hizli_soru_{i}",
                index=None
            )
        
        if st.button("📊 Sonuçları Göster", type="primary", use_container_width=True):
            # Tüm soruların cevaplanıp cevaplanmadığını kontrol et
            unanswered = [i+1 for i, a in answers.items() if a is None]
            if unanswered:
                st.warning(f"⚠️ Lütfen tüm soruları cevapla. Cevaplanmamış: {', '.join(map(str, unanswered))}")
            else:
                # Doğru sayısını hesapla
                correct = sum(1 for i, a in answers.items() if a == data['sorular'][i]['dogru'])
                
                result = calculate_speed_reading_score(wpm, correct)
                st.session_state.hizli_okuma_result = result
                st.session_state.hizli_okuma_answers = answers
                st.session_state.hizli_okuma_state = "results"
                
                # Veritabanına kaydet
                save_speed_reading_result(
                    user_id=user['id'],
                    grade=grade,
                    wpm=result['wpm'],
                    comprehension_pct=result['comprehension_pct'],
                    effective_speed=result['effective_speed'],
                    duration_seconds=duration,
                    correct_answers=correct,
                    total_questions=10
                )
                st.rerun()
    
    elif state == "results":
        result = st.session_state.hizli_okuma_result
        answers = st.session_state.hizli_okuma_answers
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 16px; padding: 2rem; color: white; text-align: center; margin-bottom: 1.5rem;">
            <h2 style="color: white; margin: 0;">📊 Test Sonuçların</h2>
            <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;">{result['level']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⚡ Okuma Hızı", f"{result['wpm']} k/dk")
        with col2:
            st.metric("🎯 Anlama Oranı", f"%{result['comprehension_pct']}")
        with col3:
            st.metric("📈 Etkili Hız", f"{result['effective_speed']}")
        
        st.markdown(f"**Doğru Cevap:** {result['correct_answers']}/{result['total_questions']}")
        
        # Cevap detayları
        with st.expander("📋 Cevap Detayları"):
            data = get_speed_reading_data(user['grade'])
            for i, q in enumerate(data['sorular']):
                user_ans = answers.get(i)
                is_correct = user_ans == q['dogru']
                icon = "✅" if is_correct else "❌"
                st.markdown(f"{icon} **{i+1}.** {q['soru']}")
                if not is_correct:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;Senin cevabın: {user_ans} → Doğru cevap: **{q['dogru']}**")
        
        if st.button("🔄 Yeni Test Yap", type="primary", use_container_width=True):
            st.session_state.hizli_okuma_state = "ready"
            for key in list(st.session_state.keys()):
                if key.startswith("hizli_"):
                    del st.session_state[key]
            st.session_state.hizli_okuma_state = "ready"
            st.rerun()


def render_gecmis_kayitlar(user):
    """Öğrencinin geçmiş kayıtlarını gösterir."""
    st.markdown("### 📊 Geçmiş Kayıtlarım")
    
    # Ses kayıtları
    st.markdown("#### 🎤 Ses Kayıtları")
    recordings = get_recordings_by_user(user['id'])
    if recordings:
        for rec in recordings:
            with st.expander(f"📅 {rec['created_at']} — {rec['text_id']}"):
                st.markdown(f"**Metin ID:** {rec['text_id']}")
                st.markdown(f"**Kayıt Tarihi:** {rec['created_at']}")
                st.info("Ses kaydın öğretmeninde mevcut. Analiz sonuçları için öğretmenine danış.")
    else:
        st.info("Henüz ses kaydın bulunmuyor. İlk kaydını yapmak için 'Okuma Hata Analizi' sekmesine git.")
    
    # Hızlı okuma sonuçları
    st.markdown("#### ⚡ Hızlı Okuma Sonuçları")
    results = get_speed_reading_results(user['id'])
    if results:
        for r in results:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Hız", f"{r['wpm']:.0f} k/dk")
            with col2:
                st.metric("Anlama", f"%{r['comprehension_pct']:.0f}")
            with col3:
                st.metric("Etkili Hız", f"{r['effective_speed']:.0f}")
            with col4:
                st.metric("Doğru", f"{r['correct_answers']}/{r['total_questions']}")
            st.markdown(f"<small style='color: #94A3B8;'>📅 {r['created_at']}</small>", unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.info("Henüz hızlı okuma testi yapmadın. '⚡ Hızlı Okuma Testi' sekmesinden başlayabilirsin.")

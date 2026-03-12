"""
Öğretmen Paneli
— Öğrenci yönetimi, ses kaydı dinleme, Whisper + Claude AI ile otomatik analiz, grafikler
"""

import streamlit as st
import base64
import plotly.graph_objects as go
import plotly.express as px
from db_utils import (
    get_all_students, get_user_by_id, get_recordings_by_user,
    get_recording_by_id, save_analysis_report, get_report_by_recording,
    get_reports_by_user, get_speed_reading_results, delete_recording
)
from okuma_hata_engine import analyze_reading_with_claude, HATA_KATEGORILERI
from speech_to_text import transcribe_audio


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
    
    st.markdown("### 👨‍🎓 Öğrenci Seçimi")
    
    grades = sorted(set(s['grade'] for s in students))
    selected_grade = st.selectbox("📚 Sınıf Filtresi", ["Tümü"] + [f"{g}. Sınıf" for g in grades])
    
    if selected_grade != "Tümü":
        grade_num = int(selected_grade.split(".")[0])
        filtered = [s for s in students if s['grade'] == grade_num]
    else:
        filtered = students
    
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
                    st.audio(audio_bytes)
                except Exception as e:
                    st.error(f"Ses kaydı oynatılamadı: {e}")
            else:
                st.warning("Ses kaydı verisi bulunamadı.")
            
            # Analiz butonu veya mevcut rapor
            if existing_report:
                # Grafik verisi varsa göster
                try:
                    import json
                    error_summary = existing_report.get('error_summary', '')
                    if error_summary:
                        chart_data = json.loads(error_summary)
                        render_analysis_charts(chart_data, student['name'])
                except Exception:
                    pass
                
                st.markdown("### 📋 Analiz Raporu")
                st.markdown(existing_report['report_markdown'])
                st.markdown(f"<small style='color: #94A3B8;'>📅 Rapor tarihi: {existing_report['created_at']}</small>", unsafe_allow_html=True)
                
                if st.button(f"🔄 Yeniden Analiz Et", key=f"reanalyze_{rec_id}"):
                    run_auto_analysis(rec_id, selected_id, student, full_rec)
            else:
                st.markdown("""
                <div style="background: #EEF2FF; border-left: 4px solid #6366F1; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                    <strong>🤖 Otomatik Analiz</strong><br>
                    Butona basınca ses kaydı <strong>Whisper AI</strong> ile otomatik metne çevrilir, 
                    ardından <strong>Claude AI</strong> detaylı okuma hata analizi yapar ve grafikler oluşturur.
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🤖 Otomatik Analiz Et", key=f"analyze_{rec_id}", type="primary"):
                    run_auto_analysis(rec_id, selected_id, student, full_rec)
            
            # Silme butonu
            st.markdown("---")
            if st.button("🗑️ Bu Kaydı Sil", key=f"del_teacher_rec_{rec_id}", type="secondary"):
                st.session_state[f"teacher_confirm_del_{rec_id}"] = True
            
            if st.session_state.get(f"teacher_confirm_del_{rec_id}"):
                st.warning("⚠️ Bu ses kaydı ve varsa analiz raporu kalıcı olarak silinecek!")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ Evet, Sil", key=f"teacher_yes_{rec_id}", type="primary"):
                        if delete_recording(rec_id):
                            st.success("Kayıt silindi!")
                            del st.session_state[f"teacher_confirm_del_{rec_id}"]
                            st.rerun()
                        else:
                            st.error("Silme sırasında hata oluştu.")
                with col_no:
                    if st.button("❌ Vazgeç", key=f"teacher_no_{rec_id}"):
                        del st.session_state[f"teacher_confirm_del_{rec_id}"]
                        st.rerun()
    
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


def run_auto_analysis(rec_id, student_id, student, full_rec):
    """Whisper + Claude AI ile tam otomatik analiz."""
    import json
    
    if not full_rec or not full_rec.get('audio_base64'):
        st.error("Ses kaydı verisi bulunamadı!")
        return
    
    progress = st.progress(0)
    
    # 1. Whisper ile otomatik transkripsiyon
    progress.progress(10, "🎤 Whisper AI ses kaydını dinliyor...")
    with st.spinner("🎤 Ses kaydı metne çevriliyor (Whisper AI)..."):
        whisper_result = transcribe_audio(full_rec['audio_base64'])
    
    if not whisper_result['success']:
        progress.progress(100, "Hata!")
        st.error(f"❌ **Whisper Transkripsiyon Hatası:** {whisper_result['error']}")
        
        # Fallback: Manuel transkripsiyon
        st.warning("⚠️ Otomatik transkripsiyon başarısız oldu. Manuel transkripsiyon ile devam edebilirsiniz.")
        transcription = st.text_area(
            "Öğrencinin okuduğu metni elle yazın:",
            height=150,
            key=f"manual_trans_{rec_id}",
            placeholder="Ses kaydını dinleyerek öğrencinin okuduğunu buraya yazın..."
        )
        if st.button("🚀 Manuel Transkript ile Analiz Et", key=f"manual_analyze_{rec_id}", type="primary"):
            if transcription and len(transcription.strip()) > 10:
                _run_claude_analysis(rec_id, student_id, student, transcription.strip(), 0, full_rec)
            else:
                st.warning("Lütfen en az 10 karakter yazın.")
        return
    
    # Transkripsiyon başarılı
    transcription = whisper_result['text']
    duration = whisper_result['duration']
    
    progress.progress(30, "✅ Transkripsiyon tamamlandı!")
    
    # Transkripsiyon sonucunu göster
    st.markdown("**🎤 Whisper AI Transkripti:**")
    st.markdown(f"""
    <div style="background: #F0FDF4; border: 2px solid #22C55E; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
        <div style="display:flex; justify-content:space-between; margin-bottom: 0.5rem;">
            <span style="color: #16A34A; font-weight: 600;">✅ Otomatik Transkripsiyon</span>
            <span style="color: #64748B; font-size: 0.85rem;">⏱️ {duration:.1f} saniye</span>
        </div>
        <div style="font-size: 1rem; line-height: 1.8; color: #1E293B;">{transcription}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Claude ile analiz
    _run_claude_analysis(rec_id, student_id, student, transcription, duration, full_rec)


def _run_claude_analysis(rec_id, student_id, student, transcription, duration, full_rec):
    """Claude AI analizi çalıştırır ve grafikleri gösterir."""
    import json
    
    progress = st.progress(40)
    progress.progress(40, "🤖 Claude AI analiz yapıyor...")
    
    with st.spinner("🤖 Claude AI detaylı analiz raporu üretiyor (30-60 saniye)..."):
        result = analyze_reading_with_claude(
            transcription=transcription,
            original_text=full_rec['original_text'],
            student_name=student['name'],
            student_grade=student['grade'],
            reading_duration_seconds=duration
        )
    
    if not result['success']:
        progress.progress(100, "Hata!")
        st.error(f"❌ **{result['error']}**")
        return
    
    progress.progress(80, "📊 Grafikler oluşturuluyor...")
    
    # Raporu ve grafik verisini kaydet
    chart_data_json = json.dumps(result['data'], ensure_ascii=False) if result['data'] else ""
    
    save_analysis_report(
        recording_id=rec_id,
        user_id=student_id,
        report_markdown=result['report'],
        error_summary=chart_data_json  # JSON verisini error_summary alanında saklıyoruz
    )
    
    progress.progress(100, "✅ Tamamlandı!")
    st.success("✅ Analiz tamamlandı ve kaydedildi!")
    
    # 3. Grafikleri göster
    if result['data']:
        render_analysis_charts(result['data'], student['name'])
    
    # 4. Raporu göster
    st.markdown("### 📋 Detaylı Analiz Raporu")
    st.markdown(result['report'])


def render_analysis_charts(data: dict, student_name: str):
    """Analiz verilerinden interaktif grafikler oluşturur."""
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 16px; padding: 1.5rem; color: white; text-align: center; margin: 1rem 0;">
        <h3 style="color: white; margin: 0;">📊 {student_name} — Okuma Analiz Grafikleri</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Üst metrikler
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        wpm = data.get('wpm', 0)
        st.metric("⚡ Okuma Hızı", f"{wpm} k/dk")
    with col2:
        accuracy = data.get('dogruluk_yuzdesi', 0)
        st.metric("🎯 Doğruluk", f"%{accuracy:.1f}")
    with col3:
        total_errors = data.get('toplam_hata', 0)
        st.metric("❌ Toplam Hata", f"{total_errors}")
    with col4:
        level = data.get('seviye', 'Belirsiz')
        st.metric("📈 Seviye", level)
    
    # Grafik satırı 1: Hata dağılımı + Profil
    col_left, col_right = st.columns(2)
    
    with col_left:
        # Hata kategorileri bar chart
        hata = data.get('hata_sayilari', {})
        if hata:
            categories = list(hata.keys())
            values = list(hata.values())
            
            colors = ['#EF4444' if v > 0 else '#D1D5DB' for v in values]
            
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=values,
                    y=categories,
                    orientation='h',
                    marker_color=colors,
                    text=values,
                    textposition='auto',
                )
            ])
            fig_bar.update_layout(
                title="📊 Hata Kategorileri Dağılımı",
                xaxis_title="Hata Sayısı",
                yaxis_title="",
                height=400,
                margin=dict(l=10, r=10, t=40, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with col_right:
        # Okuma profili radar chart
        profil = data.get('profil_puanlari', {})
        if profil:
            categories_r = list(profil.keys())
            values_r = list(profil.values())
            
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=values_r + [values_r[0]],
                theta=categories_r + [categories_r[0]],
                fill='toself',
                fillcolor='rgba(99, 102, 241, 0.3)',
                line=dict(color='#6366F1', width=2),
                marker=dict(size=8, color='#6366F1'),
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(size=10)),
                    angularaxis=dict(tickfont=dict(size=12)),
                ),
                title="📈 Okuma Profili (1-10 Puan)",
                showlegend=False,
                height=400,
                margin=dict(l=40, r=40, t=40, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_radar, use_container_width=True)
    
    # Grafik satırı 2: Doğruluk göstergesi + Hata detayları tablosu
    col_gauge, col_table = st.columns(2)
    
    with col_gauge:
        # Doğruluk gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=accuracy,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "🎯 Okuma Doğruluğu (%)", 'font': {'size': 16}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "#6366F1"},
                'steps': [
                    {'range': [0, 50], 'color': '#FEE2E2'},
                    {'range': [50, 75], 'color': '#FEF3C7'},
                    {'range': [75, 90], 'color': '#DBEAFE'},
                    {'range': [90, 100], 'color': '#DCFCE7'},
                ],
                'threshold': {
                    'line': {'color': '#22C55E', 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                },
            }
        ))
        fig_gauge.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col_table:
        # Hata detayları tablosu
        detaylar = data.get('hata_detaylari', [])
        if detaylar:
            st.markdown("**🔍 Hata Detayları:**")
            table_md = "| # | Orijinal | Okunan | Kategori | Açıklama |\n|---|----------|--------|----------|----------|\n"
            for i, d in enumerate(detaylar[:15], 1):  # Max 15 satır
                table_md += f"| {i} | {d.get('orijinal','')} | {d.get('okunan','')} | {d.get('kategori','')} | {d.get('aciklama','')} |\n"
            st.markdown(table_md)
        else:
            st.success("🎉 Hata detayı bulunamadı — harika okuma!")
    
    # Hata dağılımı pasta grafik
    hata = data.get('hata_sayilari', {})
    nonzero = {k: v for k, v in hata.items() if v > 0}
    if nonzero:
        fig_pie = go.Figure(data=[go.Pie(
            labels=list(nonzero.keys()),
            values=list(nonzero.values()),
            hole=0.4,
            marker=dict(colors=px.colors.qualitative.Set3),
            textposition='inside',
            textinfo='percent+label',
        )])
        fig_pie.update_layout(
            title="🥧 Hata Dağılımı (Oransal)",
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_pie, use_container_width=True)


def render_genel_bakis():
    """Tüm öğrencilerin genel durumu."""
    st.markdown("### 📊 Genel Bakış")
    
    students = get_all_students()
    if not students:
        st.info("Kayıtlı öğrenci bulunmuyor.")
        return
    
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
    
    st.markdown("#### 📚 Sınıf Bazlı Öğrenci Dağılımı")
    for g in sorted(grades.keys()):
        st.markdown(f"**{g}. Sınıf:** {grades[g]} öğrenci")
    
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

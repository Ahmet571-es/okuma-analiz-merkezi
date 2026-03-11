import streamlit as st
import time
import os
from db_utils import init_db, login_student, register_student, reset_student_password, repair_database

st.set_page_config(
    page_title="OKUMA ANALİZ MERKEZİ",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

init_db()

# =========================================================
# 🎨 CSS TASARIM SİSTEMİ
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');
    :root {
        --navy: #0F1B2D; --blue: #2563EB; --cyan: #06B6D4;
        --red: #DC2626; --gold: #F59E0B; --emerald: #10B981;
        --surface: #FFFFFF; --surface-alt: #F8FAFC; --border: #E2E8F0;
        --text-primary: #0F172A; --text-secondary: #475569; --text-muted: #94A3B8;
    }
    .stApp { background: var(--surface-alt) !important; font-family: 'DM Sans', sans-serif !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }
    @keyframes fadeUp { from { opacity: 0; transform: translateY(24px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes gradient-shift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .hero-container { text-align: center; padding: 30px 0 10px 0; animation: fadeUp 0.7s ease-out; }
    .hero-title {
        font-family: 'Outfit', sans-serif; font-size: 2.6rem; font-weight: 900;
        letter-spacing: 3px; text-transform: uppercase; margin: 0; line-height: 1.15;
        background: linear-gradient(135deg, var(--navy) 0%, var(--blue) 50%, var(--navy) 100%);
        background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: gradient-shift 6s ease infinite;
    }
    .hero-subtitle { font-family: 'Outfit', sans-serif; font-size: 0.92rem; color: var(--text-secondary); font-weight: 400; margin-top: 5px; letter-spacing: 2px; text-transform: uppercase; }
    .hero-divider { height: 3px; background: linear-gradient(90deg, transparent 5%, var(--blue) 30%, var(--emerald) 50%, var(--gold) 70%, transparent 95%); margin: 18px auto 26px auto; max-width: 340px; border-radius: 2px; opacity: 0.6; }
    .auth-card { background: var(--surface); border: 1px solid var(--border); border-radius: 20px; max-width: 560px; margin: 0 auto; box-shadow: 0 12px 40px rgba(15,23,42,0.12); overflow: hidden; animation: fadeUp 0.5s ease-out 0.1s both; position: relative; }
    .auth-card::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, var(--blue), var(--cyan), var(--emerald)); }
    .auth-card-body { padding: 32px 28px 24px; }
    .stButton > button { border-radius: 12px !important; padding: 11px 24px !important; font-weight: 600 !important; font-family: 'Outfit', sans-serif !important; font-size: 0.92rem !important; width: 100% !important; transition: all 0.3s ease !important; border: none !important; }
    .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 24px rgba(37,99,235,0.2) !important; }
    .stFormSubmitButton > button { border-radius: 12px !important; padding: 13px 28px !important; font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; background: linear-gradient(135deg, var(--blue) 0%, #1D4ED8 100%) !important; color: white !important; border: none !important; width: 100% !important; }
    .stTextInput > div > div > input { border-radius: 12px !important; border: 1.5px solid var(--border) !important; padding: 11px 15px !important; }
    .feature-chips { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 20px; }
    .chip { display: inline-flex; align-items: center; gap: 4px; padding: 5px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 500; font-family: 'Outfit', sans-serif; background: var(--surface); color: var(--text-secondary); border: 1px solid var(--border); }
    .version-badge { position: fixed; bottom: 10px; right: 14px; background: var(--surface); color: var(--text-muted); padding: 4px 12px; border-radius: 20px; font-size: 0.68rem; font-family: 'Outfit', sans-serif; box-shadow: 0 1px 3px rgba(15,23,42,0.06); border: 1px solid var(--border); z-index: 999; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, var(--navy) 0%, #1E3A5F 100%); }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
for key, default in [('role', None), ('student_id', None), ('student_name', None),
                     ('login_phase', 1), ('auth_mode', 'register')]:
    if key not in st.session_state:
        st.session_state[key] = default

def go_to_login(): st.session_state.auth_mode = 'login'
def go_to_register(): st.session_state.auth_mode = 'register'
def go_to_teacher(): st.session_state.auth_mode = 'teacher'
def go_to_forgot_password(): st.session_state.auth_mode = 'forgot_password'

def get_teacher_password():
    try:
        if "teacher_password" in st.secrets: return st.secrets["teacher_password"]
    except: pass
    return os.getenv("TEACHER_PASSWORD")


# =========================================================
# HERO HEADER
# =========================================================
def render_hero_header():
    st.markdown("""
        <div class="hero-container">
            <div style="font-size: 4rem; margin-bottom: 10px;">📖</div>
            <div class="hero-title">Okuma Analiz Merkezi</div>
            <div class="hero-subtitle">Sesli Okuma Hata Analizi & Hızlı Okuma Testi</div>
        </div>
        <div class="hero-divider"></div>
    """, unsafe_allow_html=True)


# =========================================================
# ANA GİRİŞ SİSTEMİ
# =========================================================
def main_auth_flow():
    render_hero_header()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        mode = st.session_state.auth_mode

        if mode == 'register':
            st.markdown('<div class="auth-card"><div class="auth-card-body">', unsafe_allow_html=True)
            st.markdown("### 📝 Yeni Öğrenci Kaydı")
            st.caption("Testlere katılmak için profilini oluştur.")
            with st.form("register_form"):
                name = st.text_input("👤 Ad Soyad", placeholder="Tam adını yaz...")
                c1, c2, c3 = st.columns(3)
                age = c1.number_input("🎂 Yaş", min_value=5, max_value=99, step=1, value=10)
                grade = c2.selectbox("🎓 Sınıf", options=[1,2,3,4,5,6,7,8], index=3)
                gender = c3.selectbox("⚧ Cinsiyet", ["Kız", "Erkek"])
                new_user = st.text_input("📧 E-posta", placeholder="ornek@email.com")
                new_pw = st.text_input("🔒 Şifre", type="password", placeholder="En az 4 karakter")
                secret_word = st.text_input("🛡️ Kurtarma Kelimesi", placeholder="Şifreni unutursan lazım olacak")
                submit = st.form_submit_button("🚀 Kayıt Ol", type="primary")
                if submit:
                    import re
                    if not name or not new_user or not new_pw or not secret_word:
                        st.warning("⚠️ Tüm alanları doldurun.")
                    elif len(new_pw) < 4:
                        st.warning("⚠️ Şifre en az 4 karakter.")
                    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_user.strip()):
                        st.warning("⚠️ Geçerli e-posta girin.")
                    else:
                        success, result = register_student(name.title(), new_user.strip().lower(), new_pw, age, gender, secret_word.lower().strip(), grade)
                        if success:
                            st.success("✅ Kayıt Başarılı!")
                            time.sleep(1.5)
                            st.session_state.auth_mode = 'login'
                            st.rerun()
                        else:
                            st.error(result)
            st.markdown('</div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            lc1, lc2 = st.columns(2)
            lc1.button("🔑 Giriş Yap", on_click=go_to_login)
            lc2.button("👨‍🏫 Öğretmen Girişi", on_click=go_to_teacher)

        elif mode == 'login':
            st.markdown('<div class="auth-card"><div class="auth-card-body">', unsafe_allow_html=True)
            st.markdown("### 🔓 Tekrar Hoşgeldin!")
            with st.form("login_form"):
                user = st.text_input("📧 E-posta", placeholder="E-posta adresini gir...")
                pw = st.text_input("🔒 Şifre", type="password")
                submit = st.form_submit_button("Giriş Yap ➡️", type="primary")
                if submit:
                    if not user or not pw:
                        st.warning("⚠️ Boş bırakılamaz.")
                    else:
                        status, student_obj = login_student(user.strip().lower(), pw)
                        if status:
                            st.success(f"🎉 Hoşgeldin {student_obj.name}!")
                            st.session_state.role = "student"
                            st.session_state.student_id = student_obj.id
                            st.session_state.student_name = student_obj.name
                            st.session_state.student_age = student_obj.age
                            st.session_state.student_grade = student_obj.grade
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("❌ E-posta veya şifre hatalı.")
            st.markdown('</div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            lc1, lc2 = st.columns(2)
            lc1.button("📝 Kayıt Ol", on_click=go_to_register)
            lc2.button("❓ Şifremi Unuttum", on_click=go_to_forgot_password)

        elif mode == 'forgot_password':
            st.markdown('<div class="auth-card"><div class="auth-card-body">', unsafe_allow_html=True)
            st.markdown("### 🔐 Şifre Sıfırlama")
            with st.form("forgot_form"):
                user = st.text_input("📧 E-posta")
                secret = st.text_input("🛡️ Kurtarma Kelimesi", type="password")
                new_pw = st.text_input("🔒 Yeni Şifre", type="password")
                submit = st.form_submit_button("Şifremi Yenile ✅", type="primary")
                if submit:
                    if not user or not secret or not new_pw:
                        st.warning("⚠️ Tüm alanları doldurun.")
                    else:
                        success, msg = reset_student_password(user.strip().lower(), secret, new_pw)
                        if success:
                            st.success("✅ Şifre güncellendi!")
                            time.sleep(1.5)
                            st.session_state.auth_mode = 'login'
                            st.rerun()
                        else:
                            st.error(msg)
            st.markdown('</div></div>', unsafe_allow_html=True)
            st.button("⬅️ Giriş Ekranı", on_click=go_to_login)

        elif mode == 'teacher':
            st.markdown('<div class="auth-card"><div class="auth-card-body">', unsafe_allow_html=True)
            st.markdown("### 👨‍🏫 Öğretmen Paneli")
            with st.form("teacher_form"):
                pw = st.text_input("🔑 Yönetici Şifresi", type="password")
                submit = st.form_submit_button("Panele Git ➡️", type="primary")
                if submit:
                    secret_pass = get_teacher_password()
                    if secret_pass is None:
                        st.error("⚠️ Şifre yapılandırılmamış.")
                    elif pw == secret_pass:
                        st.session_state.role = "teacher"
                        st.rerun()
                    else:
                        st.error("❌ Hatalı şifre.")
            st.markdown('</div></div>', unsafe_allow_html=True)
            st.button("⬅️ Öğrenci Ekranı", on_click=go_to_register)

        st.markdown("""
            <div class="feature-chips">
                <span class="chip">📖 Okuma Hata Analizi</span>
                <span class="chip">🎙️ Sesli Okuma</span>
                <span class="chip">⏱️ Hızlı Okuma Testi</span>
                <span class="chip">🤖 AI Destekli Analiz</span>
                <span class="chip">📊 Detaylı Rapor</span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="version-badge">OKUMA ANALİZ MERKEZİ v1.0</div>', unsafe_allow_html=True)


# =========================================================
# YÖNLENDİRME
# =========================================================
if st.session_state.role is None:
    main_auth_flow()
elif st.session_state.role == "student":
    import student_view
    student_view.app()
elif st.session_state.role == "teacher":
    import teacher_view
    teacher_view.app()

# SIDEBAR
if st.session_state.role:
    with st.sidebar:
        user_name = st.session_state.get('student_name', 'Yönetici')
        role_label = "👨‍🏫 Yönetici" if st.session_state.role == "teacher" else "🎓 Öğrenci"
        st.markdown(f"""
            <div style="text-align:center; padding: 14px 0;">
                <div style="font-size: 2.2rem;">{'👨‍🏫' if st.session_state.role == 'teacher' else '📖'}</div>
                <div style="font-size: 1.15rem; font-weight: 700; margin-top: 6px;">{user_name}</div>
                <div style="font-size: 0.78rem; color: rgba(255,255,255,0.6); margin-top: 3px;">{role_label}</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        if st.session_state.role == "teacher":
            if st.button("🔧 Veritabanını Onar"):
                if repair_database():
                    st.success("✅ Onarıldı!")
                    time.sleep(1)
                    st.rerun()
            st.markdown("---")
        if st.button("🚪 Güvenli Çıkış"):
            st.session_state.clear()
            st.session_state.auth_mode = 'register'
            st.rerun()

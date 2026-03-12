"""
Okuma Analiz Merkezi — Ana Uygulama
Öğrenci girişi, kayıt, öğretmen paneli, yönlendirme
"""

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

# Sayfa yapılandırması
st.set_page_config(
    page_title="Okuma Analiz Merkezi",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Veritabanını başlat
from db_utils import init_db, register_user, login_user, reset_password
init_db()

# ─── CSS STİLLERİ ────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=DM+Sans:wght@400;500;700&display=swap');
    
    /* Ana font */
    html, body, .stApp, .stMarkdown, p, span, div, label {
        font-family: 'DM Sans', sans-serif !important;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
    }
    
    /* Ana arka plan */
    .stApp {
        background: linear-gradient(180deg, #F0F2F6 0%, #E8EBF0 100%);
    }
    
    /* Sidebar gizle */
    section[data-testid="stSidebar"] { display: none; }
    
    /* Buton stilleri */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-family: 'DM Sans', sans-serif !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
        color: white !important;
        border: none !important;
    }
    
    /* Tab stilleri */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    
    /* Input stilleri */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        border-radius: 10px !important;
        border: 2px solid #E2E8F0 !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
    }
    
    /* Metric stilleri */
    [data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        color: #6366F1 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366F1, #8B5CF6) !important;
    }
    
    /* Footer */
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─── SESSION STATE ────────────────────────────────────────────────────────────

if "user" not in st.session_state:
    st.session_state.user = None
if "is_teacher" not in st.session_state:
    st.session_state.is_teacher = False
if "page" not in st.session_state:
    st.session_state.page = "login"


# ─── HEADER ──────────────────────────────────────────────────────────────────

def render_header():
    """Üst logo ve navigasyon."""
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem 0;">
            <h1 style="background: linear-gradient(135deg, #6366F1, #8B5CF6, #A855F7);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       font-size: 2.2rem; margin: 0; letter-spacing: -0.5px;">
                📖 Okuma Analiz Merkezi
            </h1>
            <p style="color: #64748B; margin-top: 0.3rem; font-size: 1rem;">
                Sesli Okuma Hata Analizi & Hızlı Okuma Testi
            </p>
        </div>
        """, unsafe_allow_html=True)


# ─── GİRİŞ SAYFASI ──────────────────────────────────────────────────────────

def render_login_page():
    """Giriş sayfası."""
    render_header()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background: white; border-radius: 20px; padding: 2rem; 
                    box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
        """, unsafe_allow_html=True)
        
        login_tab, register_tab, teacher_tab, reset_tab = st.tabs([
            "🔑 Öğrenci Girişi", "📝 Kayıt Ol", "🏫 Öğretmen Girişi", "🔄 Şifre Sıfırla"
        ])
        
        with login_tab:
            render_student_login()
        
        with register_tab:
            render_register()
        
        with teacher_tab:
            render_teacher_login()
        
        with reset_tab:
            render_password_reset()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Veritabanı durum göstergesi
        try:
            from db_utils import check_db_status
            db_info = check_db_status()
            if db_info.get("db_type") == "postgresql":
                st.caption("🟢 Veritabanı: PostgreSQL (veriler kalıcı)")
            else:
                st.caption("🟡 Veritabanı: SQLite (⚠️ veriler yeniden başlatmada kaybolur)")
        except Exception:
            pass


def render_student_login():
    """Öğrenci giriş formu."""
    st.markdown("#### 🔑 Öğrenci Girişi")
    
    email = st.text_input("📧 E-posta", key="login_email", placeholder="ornek@email.com")
    password = st.text_input("🔒 Şifre", type="password", key="login_password")
    
    if st.button("Giriş Yap", type="primary", use_container_width=True, key="login_btn"):
        if not email or not password:
            st.warning("Lütfen tüm alanları doldurun.")
            return
        
        user = login_user(email, password)
        if user:
            st.session_state.user = user
            st.session_state.is_teacher = False
            st.session_state.page = "student"
            st.success(f"✅ Hoş geldin, {user['name']}!")
            st.rerun()
        else:
            st.error("❌ E-posta veya şifre hatalı.")


def render_register():
    """Kayıt formu."""
    st.markdown("#### 📝 Yeni Kayıt")
    
    name = st.text_input("👤 Ad Soyad", key="reg_name", placeholder="Ali Yılmaz")
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("🎂 Yaş", min_value=5, max_value=18, value=10, key="reg_age")
    with col2:
        grade = st.selectbox("📚 Sınıf", list(range(1, 9)), index=3, key="reg_grade", format_func=lambda x: f"{x}. Sınıf")
    
    gender = st.selectbox("⚧ Cinsiyet", ["Erkek", "Kız"], key="reg_gender")
    email = st.text_input("📧 E-posta", key="reg_email", placeholder="ornek@email.com")
    
    col1, col2 = st.columns(2)
    with col1:
        password = st.text_input("🔒 Şifre", type="password", key="reg_password")
    with col2:
        password2 = st.text_input("🔒 Şifre Tekrar", type="password", key="reg_password2")
    
    recovery = st.text_input("🔑 Kurtarma Kelimesi", key="reg_recovery", 
                             placeholder="Şifrenizi unutursanız kullanacağınız kelime",
                             help="Şifrenizi unutursanız bu kelime ile sıfırlayabilirsiniz.")
    
    if st.button("Kayıt Ol", type="primary", use_container_width=True, key="reg_btn"):
        if not all([name, email, password, password2, recovery]):
            st.warning("Lütfen tüm alanları doldurun.")
            return
        if password != password2:
            st.error("❌ Şifreler eşleşmiyor.")
            return
        if len(password) < 4:
            st.error("❌ Şifre en az 4 karakter olmalı.")
            return
        
        success, msg = register_user(name, age, grade, gender, email, password, recovery)
        if success:
            st.success(f"✅ {msg} Şimdi giriş yapabilirsin.")
        else:
            st.error(f"❌ {msg}")


def render_teacher_login():
    """Öğretmen giriş formu."""
    st.markdown("#### 🏫 Öğretmen Girişi")
    
    teacher_pw = st.text_input("🔒 Öğretmen Şifresi", type="password", key="teacher_password")
    
    if st.button("Öğretmen Girişi", type="primary", use_container_width=True, key="teacher_btn"):
        correct_pw = os.environ.get("TEACHER_PASSWORD", "")
        if not correct_pw:
            try:
                correct_pw = st.secrets.get("TEACHER_PASSWORD", "")
            except Exception:
                pass
        
        if not correct_pw:
            st.error("❌ Öğretmen şifresi yapılandırılmamış. TEACHER_PASSWORD ortam değişkenini ayarlayın.")
            return
        
        if teacher_pw == correct_pw:
            st.session_state.is_teacher = True
            st.session_state.page = "teacher"
            st.success("✅ Öğretmen girişi başarılı!")
            st.rerun()
        else:
            st.error("❌ Şifre hatalı.")


def render_password_reset():
    """Şifre sıfırlama formu."""
    st.markdown("#### 🔄 Şifre Sıfırla")
    
    email = st.text_input("📧 E-posta", key="reset_email", placeholder="ornek@email.com")
    recovery = st.text_input("🔑 Kurtarma Kelimesi", key="reset_recovery")
    new_pw = st.text_input("🔒 Yeni Şifre", type="password", key="reset_newpw")
    
    if st.button("Şifreyi Sıfırla", type="primary", use_container_width=True, key="reset_btn"):
        if not all([email, recovery, new_pw]):
            st.warning("Lütfen tüm alanları doldurun.")
            return
        if len(new_pw) < 4:
            st.error("❌ Şifre en az 4 karakter olmalı.")
            return
        
        success, msg = reset_password(email, recovery, new_pw)
        if success:
            st.success(f"✅ {msg}")
        else:
            st.error(f"❌ {msg}")


# ─── ÇIKIŞ BUTONU ────────────────────────────────────────────────────────────

def render_logout():
    """Çıkış butonu."""
    col1, col2, col3 = st.columns([6, 2, 1])
    with col3:
        if st.button("🚪 Çıkış", key="logout_btn"):
            # Session temizle
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ─── ANA ROUTING ─────────────────────────────────────────────────────────────

def main():
    """Ana uygulama yönlendirmesi."""
    page = st.session_state.get("page", "login")
    
    if page == "login":
        render_login_page()
    
    elif page == "student":
        if st.session_state.get("user"):
            render_logout()
            from student_view import render_student_view
            render_student_view()
        else:
            st.session_state.page = "login"
            st.rerun()
    
    elif page == "teacher":
        if st.session_state.get("is_teacher"):
            render_logout()
            from teacher_view import render_teacher_view
            render_teacher_view()
        else:
            st.session_state.page = "login"
            st.rerun()
    
    else:
        st.session_state.page = "login"
        st.rerun()
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 1rem; color: #94A3B8; font-size: 0.85rem;">
        📖 Okuma Analiz Merkezi — AI Destekli Okuma Hata Analizi<br>
        <span style="font-size: 0.75rem;">Powered by Claude AI • Otonom Reklam Ajansı</span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

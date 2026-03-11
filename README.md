# 📖 Okuma Analiz Merkezi

AI destekli sesli okuma hata analizi ve hızlı okuma testi platformu.

## 🎯 Özellikler

### Öğrenci Tarafı
- **Sesli Okuma Kaydı** — Sınıf düzeyine uygun metin + tarayıcıdan mikrofon kaydı
- **Hızlı Okuma Testi** — Zamanlı okuma + 10 anlama sorusu + skor hesaplama
- **Geçmiş Kayıtlar** — Önceki kayıt ve test sonuçlarını görüntüleme

### Öğretmen Tarafı
- **Öğrenci Yönetimi** — Sınıf filtreli öğrenci listesi
- **Ses Kaydı Dinleme** — Öğrenci kayıtlarını tarayıcıdan dinleme
- **🤖 Claude AI Analizi** — 10 hata kategorisinde detaylı okuma analiz raporu
- **Genel İstatistikler** — Sınıf bazlı öğrenci ve kayıt istatistikleri

### AI Analiz Raporu İçeriği
- Tam transkripsiyon ve metin karşılaştırması
- 10 hata kategorisinde sayısal ve detaylı analiz
- Okuma hızı değerlendirmesi (kelime/dakika)
- Okuma profili (akıcılık, prozodi, özgüven, dikkat)
- Güçlü yönler ve gelişim alanları
- Öğrenci, aile ve öğretmen için öneriler
- Günlük/haftalık egzersiz planı

## 🚀 Kurulum

### 1. Bağımlılıkları yükle
```bash
pip install -r requirements.txt
```

### 2. Ortam değişkenlerini ayarla

**Streamlit Cloud için** `.streamlit/secrets.toml` oluştur:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
TEACHER_PASSWORD = "ogretmen123"
```

**Yerel geliştirme için** `.env` dosyası oluştur:
```
ANTHROPIC_API_KEY=sk-ant-...
TEACHER_PASSWORD=ogretmen123
```

### 3. Uygulamayı başlat
```bash
streamlit run app.py
```

## 📁 Dosya Yapısı
```
app.py                  — Ana uygulama (giriş/kayıt/yönlendirme)
student_view.py         — Öğrenci arayüzü (metin + ses kaydı)
teacher_view.py         — Öğretmen paneli (kayıt dinleme + AI analiz)
okuma_hata_engine.py    — Metinler + hata kategorileri + AI prompt
hizli_okuma_engine.py   — Hızlı okuma testi motoru
db_utils.py             — Veritabanı işlemleri (SQLite/PostgreSQL)
requirements.txt        — Bağımlılıklar
.env.example            — Ortam değişkenleri şablonu
.streamlit/config.toml  — Tema ayarları
```

## 🔐 Güvenlik
- Şifreler SHA-256 ile hash'lenir
- Öğretmen şifresi ortam değişkeninden alınır
- Kurtarma kelimesi ile şifre sıfırlama
- API anahtarı ortam değişkeni veya Streamlit secrets

## 📊 Hata Kategorileri
1. 🔤 Harf Hatası
2. 📎 Hece Hatası
3. ❌ Kelime Hatası
4. ⏭️ Atlama Hatası
5. ➕ Ekleme Hatası
6. 🔁 Tekrar Hatası
7. 🔄 Ters Çevirme Hatası
8. 💨 Nefes/Durak Hatası
9. 🎵 Vurgu/Tonlama Hatası
10. ⏱️ Hız Hatası

## 🛠️ Teknoloji
- **Frontend:** Streamlit 1.44.1
- **AI:** Claude API (claude-sonnet-4-20250514)
- **Veritabanı:** SQLite (varsayılan) / PostgreSQL (Supabase)
- **Ses Kaydı:** Streamlit st.audio_input() (native)

---
📖 Okuma Analiz Merkezi — Powered by Claude AI • Otonom Reklam Ajansı

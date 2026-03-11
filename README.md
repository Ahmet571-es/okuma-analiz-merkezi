# 📖 Okuma Analiz Merkezi

Sesli okuma hata analizi ve hızlı okuma testi sunan, **AI destekli** Streamlit uygulaması.

## 🎙️ Testler

| Test | Açıklama |
|------|----------|
| **Okuma Hata Analizi** | Öğrenci metni sesli okur → AI transkripsiyon ve karşılaştırma → 10 hata kategorisinde detaylı analiz |
| **Hızlı Okuma Testi** | Zamanlı okuma + 10 anlama sorusu → Kelime/Dakika + Anlama yüzdesi |

## 📊 Okuma Hata Kategorileri

| # | Kategori | Açıklama |
|---|----------|----------|
| 1 | 🔤 Harf Hatası | Harflerin yanlış okunması |
| 2 | 📎 Hece Hatası | Hecelerin yanlış bölünmesi |
| 3 | ❌ Kelime Hatası | Kelimenin tamamen farklı okunması |
| 4 | ⏭️ Atlama Hatası | Kelime/satır atlanması |
| 5 | ➕ Ekleme Hatası | Metinde olmayan kelime eklenmesi |
| 6 | 🔁 Tekrar Hatası | Gereksiz tekrarlama |
| 7 | 🔄 Ters Çevirme | Harf/hece sırası değişimi |
| 8 | 💨 Nefes Hatası | Yanlış yerde durma |
| 9 | 🎵 Vurgu Hatası | Yanlış vurgu ve tonlama |
| 10 | ⏱️ Hız Hatası | Çok yavaş/hızlı okuma |

## 🎓 Desteklenen Sınıflar

1. - 8. sınıf (her sınıfa uygun metin uzunluğu)

## 🚀 Kurulum

```bash
git clone https://github.com/Ahmet571-es/okuma-analiz-merkezi.git
cd okuma-analiz-merkezi
pip install -r requirements.txt
cp .env.example .env
# .env dosyasını düzenle
streamlit run app.py
```

## ⚙️ Ortam Değişkenleri

| Değişken | Zorunlu | Açıklama |
|----------|---------|----------|
| `ANTHROPIC_API_KEY` | ✅ | Claude API anahtarı |
| `TEACHER_PASSWORD` | ✅ | Öğretmen paneli şifresi |
| `SUPABASE_DB_URL` | ❌ | PostgreSQL URL (yoksa SQLite) |
| `CLAUDE_MODEL` | ❌ | Model adı (varsayılan: claude-sonnet-4-20250514) |

## 🛠️ Teknolojiler

- **Frontend:** Streamlit
- **AI:** Anthropic Claude API (claude-sonnet-4-20250514)
- **Veritabanı:** PostgreSQL (Supabase) / SQLite
- **Dil:** Python 3.10+

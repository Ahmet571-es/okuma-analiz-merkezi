"""
Okuma Hata Analizi Motoru
— Sınıf bazlı metinler, hata kategorileri, Claude AI prompt
"""

import os
import base64
import anthropic

# ─── HATA KATEGORİLERİ ───────────────────────────────────────────────────────

HATA_KATEGORILERI = [
    {"id": 1, "emoji": "🔤", "ad": "Harf Hatası", "aciklama": "Harflerin yanlış okunması (b→d, m→n vb.)"},
    {"id": 2, "emoji": "📎", "ad": "Hece Hatası", "aciklama": "Hecelerin yanlış bölünmesi veya birleştirilmesi"},
    {"id": 3, "emoji": "❌", "ad": "Kelime Hatası", "aciklama": "Kelimenin tamamen farklı okunması"},
    {"id": 4, "emoji": "⏭️", "ad": "Atlama Hatası", "aciklama": "Kelime veya satır atlanması"},
    {"id": 5, "emoji": "➕", "ad": "Ekleme Hatası", "aciklama": "Metinde olmayan kelime eklenmesi"},
    {"id": 6, "emoji": "🔁", "ad": "Tekrar Hatası", "aciklama": "Kelimelerin gereksiz tekrarlanması"},
    {"id": 7, "emoji": "🔄", "ad": "Ters Çevirme Hatası", "aciklama": "Harf veya hece sırasının değiştirilmesi"},
    {"id": 8, "emoji": "💨", "ad": "Nefes/Durak Hatası", "aciklama": "Yanlış yerde durma veya nefes alma"},
    {"id": 9, "emoji": "🎵", "ad": "Vurgu/Tonlama Hatası", "aciklama": "Yanlış vurgu, monoton okuma, prozodi eksikliği"},
    {"id": 10, "emoji": "⏱️", "ad": "Hız Hatası", "aciklama": "Çok yavaş veya çok hızlı okuma"},
]

# ─── SINIF BAZLI METİNLER ────────────────────────────────────────────────────

SINIF_METINLERI = {
    1: {
        "id": "sinif1_metin1",
        "baslik": "Küçük Kedi",
        "metin": (
            "Bir küçük kedi vardı. Adı Pamuk'tu. Pamuk beyaz ve yumuşacıktı. "
            "Her sabah bahçeye çıkardı. Çiçeklerin arasında koşardı. Kelebeklerle oynardı. "
            "Akşam olunca eve dönerdi. Sıcak sütünü içerdi. Sonra yatağına kıvrılırdı. "
            "Pamuk çok mutlu bir kediydi."
        ),
        "kelime_sayisi": 42,
    },
    2: {
        "id": "sinif2_metin1",
        "baslik": "Orman Gezisi",
        "metin": (
            "Ali ve Ayşe bir gün ormana gezmeye gittiler. Ağaçlar çok büyük ve yeşildi. "
            "Kuşlar dallardan şarkı söylüyordu. Ali bir sincap gördü. Sincap ağaca hızla tırmandı. "
            "Ayşe yerde güzel çiçekler topladı. İkisi de çok eğlendi. Bir derede su içtiler. "
            "Su çok soğuk ve temizdi. Anneleri onlara sandviç hazırlamıştı. Ağacın altında piknik yaptılar. "
            "Akşam olunca mutlu bir şekilde eve döndüler."
        ),
        "kelime_sayisi": 68,
    },
    3: {
        "id": "sinif3_metin1",
        "baslik": "Deniz Yıldızı",
        "metin": (
            "Geçen yaz ailecek deniz kenarına tatile gittik. Sabah erkenden kumsala indik. "
            "Kumlar sıcacıktı ve ayaklarımız gömülüyordu. Deniz masmaviydi, dalgalar hafif hafif kıyıya vuruyordu. "
            "Ben kumsalda yürürken parlak bir şey gördüm. Eğilip baktım, bir deniz yıldızıydı! "
            "Turuncu renkliydi ve beş kolu vardı. Çok şaşırdım çünkü daha önce hiç gerçek deniz yıldızı görmemiştim. "
            "Babam yanıma geldi ve deniz yıldızlarının denizde yaşadığını anlattı. Onu dikkatlice denize geri bıraktım. "
            "Deniz yıldızı yavaşça suyun içinde kayboldu. O gün çok güzel bir anı biriktirdim."
        ),
        "kelime_sayisi": 96,
    },
    4: {
        "id": "sinif4_metin1",
        "baslik": "Küçük Mucit",
        "metin": (
            "Elif, mahallesinde herkesin tanıdığı meraklı bir çocuktu. Boş zamanlarında hep bir şeyler "
            "icat etmeye çalışırdı. Garajdaki eski eşyaları birleştirerek ilginç aletler yapardı. "
            "Bir gün okulda öğretmeni bilim fuarı olacağını söyledi. Elif çok heyecanlandı ve hemen "
            "bir proje düşünmeye başladı. Evdeki eski bir vantilatörü, birkaç pili ve küçük bir motoru "
            "kullanarak rüzgârla çalışan bir araba yapmaya karar verdi.\n\n"
            "Haftalarca çalıştı. Bazen parçalar kırıldı, bazen motor çalışmadı. Ama Elif hiç pes etmedi. "
            "Her başarısızlıktan bir şey öğrendi. Sonunda arabası çalıştığında gözleri parladı. "
            "Bilim fuarında jüri üyeleri Elif'in projesini çok beğendi. Birinci olmasına rağmen Elif "
            "için en güzel ödül, bir şeyi kendi başına başarmanın verdiği mutluluktu. O gün Elif, "
            "gerçek başarının pes etmemekte olduğunu anladı."
        ),
        "kelime_sayisi": 132,
    },
    5: {
        "id": "sinif5_metin1",
        "baslik": "Kapadokya'nın Sırları",
        "metin": (
            "Türkiye'nin tam ortasında, Nevşehir ilinde büyüleyici bir bölge vardır: Kapadokya. "
            "Milyonlarca yıl önce yanardağlar lav ve kül püskürttü. Zamanla rüzgâr ve yağmur bu "
            "yumuşak kayaları oyarak peri bacaları denilen ilginç şekiller oluşturdu. Bu doğal yapılar "
            "dünyada başka hiçbir yerde görülmez.\n\n"
            "Kapadokya sadece doğal güzellikleriyle değil, tarihiyle de ünlüdür. Binlerce yıl önce "
            "insanlar bu yumuşak kayaları oyarak yeraltı şehirleri inşa ettiler. Derinkuyu ve Kaymaklı "
            "gibi yeraltı şehirlerinde odalar, tüneller, havalandırma bacaları ve hatta kiliseler bulunur. "
            "Bu şehirler, insanların düşmanlardan korunmak için sığındığı güvenli alanlardı.\n\n"
            "Bugün Kapadokya, sıcak hava balonlarıyla dünyaca ünlüdür. Her sabah yüzlerce rengarenk balon "
            "gökyüzüne yükselir. Balonlardan peri bacalarını ve vadileri seyretmek unutulmaz bir deneyimdir. "
            "Her yıl milyonlarca turist bu eşsiz bölgeyi ziyaret eder. Kapadokya, doğanın ve insanın "
            "birlikte yarattığı muhteşem bir sanat eseridir."
        ),
        "kelime_sayisi": 158,
    },
    6: {
        "id": "sinif6_metin1",
        "baslik": "Yapay Zekânın Dünyası",
        "metin": (
            "Günümüzde teknoloji hayatımızın her alanına girmiş durumda. Bunların arasında en çok "
            "konuşulanı ise yapay zekâ. Peki yapay zekâ tam olarak nedir? Basitçe söylemek gerekirse, "
            "yapay zekâ bilgisayarların insanlar gibi düşünmesini, öğrenmesini ve karar vermesini "
            "sağlayan teknolojilerin genel adıdır.\n\n"
            "Yapay zekâ aslında hayatımızda farkında olmadığımız birçok yerde kullanılıyor. Telefonumuzdaki "
            "sesli asistanlar, sosyal medyadaki öneriler, otomatik çeviri programları ve hatta bazı oyunlar "
            "yapay zekâ teknolojisiyle çalışır. Hastanelerde doktorlara teşhis koymada yardımcı olur, "
            "fabrikalarda robotlar ürünleri kontrol eder.\n\n"
            "Ancak yapay zekânın bazı riskleri de var. İnsanların işlerini kaybetme korkusu, gizlilik "
            "sorunları ve yapay zekânın yanlış kararlar vermesi gibi endişeler tartışılıyor. Uzmanlar, "
            "yapay zekânın insanların yerini almayacağını, aksine onlara yardımcı olacağını söylüyor. "
            "Önemli olan, bu teknolojiyi doğru ve sorumlu bir şekilde kullanmayı öğrenmektir.\n\n"
            "Gelecekte yapay zekâ daha da gelişecek. Belki bir gün evdeki robotlar bize yemek yapacak, "
            "ödevlerimize yardım edecek ya da sağlık sorunlarımızı önceden tespit edecek. Ancak unutmamamız "
            "gereken en önemli şey, teknolojiyi üreten ve yönlendirenin her zaman insan olduğudur."
        ),
        "kelime_sayisi": 192,
    },
    7: {
        "id": "sinif7_metin1",
        "baslik": "Okyanusların Derinliklerinde",
        "metin": (
            "Dünya yüzeyinin yaklaşık yüzde yetmişi sularla kaplıdır ve okyanuslar gezegenimizin en büyük "
            "yaşam alanlarıdır. Ancak bu engin su kütlelerinin büyük bir kısmı hâlâ keşfedilmemiştir. "
            "Bilim insanları, okyanusların yüzde sekseninden fazlasının henüz haritalanmadığını ve "
            "incelenmediğini belirtiyor. Bu oran, Mars yüzeyinin bile okyanuslarımızdan daha iyi "
            "bilindiği anlamına geliyor.\n\n"
            "Okyanus derinliklerine indikçe koşullar dramatik şekilde değişir. Işık ilk iki yüz metrede "
            "tamamen kaybolur ve sıcaklık donma noktasına yaklaşır. Derinlerdeki basınç ise inanılmaz "
            "derecede yüksektir; en derin nokta olan Mariana Çukuru'nda basınç, deniz seviyesinin bin "
            "katından fazladır. Bu zorlu koşullara rağmen yaşam buralara bile ulaşmıştır.\n\n"
            "Derin deniz canlıları, karanlığa uyum sağlamak için biyolüminesans adı verilen kendi ışığını "
            "üretme yeteneği geliştirmiştir. Dev mürekkep balıkları, şeffaf denizanaları ve volkanik "
            "bacaların etrafında yaşayan tüp solucanları bu ekosistemin şaşırtıcı sakinleridir.\n\n"
            "Okyanusları araştırmak, uzay keşfi kadar heyecan verici ve önemlidir. Her dalışta yeni türler "
            "keşfediliyor, bilinmeyen ekosistemler ortaya çıkıyor. Okyanuslar, gezegenimizin son büyük "
            "keşfedilmemiş sınırıdır ve gelecekte bize henüz hayal bile edemediğimiz sırlar sunacaktır."
        ),
        "kelime_sayisi": 196,
    },
    8: {
        "id": "sinif8_metin1",
        "baslik": "Eleştirel Düşünmenin Gücü",
        "metin": (
            "Bilgi çağında yaşıyoruz. Her gün cep telefonlarımızdan, bilgisayarlarımızdan ve sosyal medyadan "
            "binlerce bilgi akışına maruz kalıyoruz. Ancak bu bilgilerin hepsi doğru mu? İşte tam bu noktada "
            "eleştirel düşünme becerisi devreye giriyor. Eleştirel düşünme, karşılaştığımız bilgileri sorgulamak, "
            "analiz etmek ve mantıklı sonuçlara ulaşmak için kullandığımız zihinsel bir süreçtir.\n\n"
            "Tarih boyunca en büyük buluşlar, mevcut bilgileri sorgulayan insanlar tarafından yapılmıştır. "
            "Galileo, dünyanın düz olduğu inancını sorguladı. Darwin, türlerin değişmez olduğu fikrini "
            "reddetti. Einstein, Newton fiziğinin ötesine geçerek göreliliği keşfetti. Bu bilim insanlarının "
            "ortak noktası, herkesle aynı şeylere baktıklarında farklı sorular sorma cesaretidir.\n\n"
            "Günlük hayatta eleştirel düşünme, sosyal medyada karşılaştığımız haberlerin doğruluğunu "
            "sorgulamaktan, reklamlardaki iddiaları değerlendirmeye kadar geniş bir alanda işe yarar. "
            "Bir iddia gördüğümüzde kendimize şu soruları sormalıyız: Bu bilginin kaynağı nedir? "
            "Kanıtlar yeterli mi? Alternatif açıklamalar olabilir mi? Bu sorular, bizi manipülasyondan "
            "ve yanlış bilgiden korur.\n\n"
            "Eleştirel düşünme bir kas gibidir; kullandıkça güçlenir. Kitap okumak, farklı bakış açılarını "
            "dinlemek, tartışmalara katılmak ve kendi fikirlerimizi bile sorgulamak bu beceriyi geliştirir. "
            "Önemli olan, her zaman meraklı ve açık fikirli kalmak, aynı zamanda kanıt olmadan hiçbir şeyi "
            "kabul etmemektir. Eleştirel düşünen bireyler, hem kendi hayatlarında daha iyi kararlar alır "
            "hem de topluma daha bilinçli bireyler olarak katkıda bulunur."
        ),
        "kelime_sayisi": 232,
    },
}

# ─── SINIF NORMLARI (Kelime/Dakika) ──────────────────────────────────────────

SINIF_NORMLARI = {
    1: {"dusuk": 20, "orta": 40, "iyi": 60, "cok_iyi": 80},
    2: {"dusuk": 40, "orta": 60, "iyi": 80, "cok_iyi": 100},
    3: {"dusuk": 60, "orta": 80, "iyi": 100, "cok_iyi": 120},
    4: {"dusuk": 70, "orta": 90, "iyi": 120, "cok_iyi": 140},
    5: {"dusuk": 80, "orta": 100, "iyi": 130, "cok_iyi": 150},
    6: {"dusuk": 90, "orta": 110, "iyi": 140, "cok_iyi": 160},
    7: {"dusuk": 100, "orta": 120, "iyi": 150, "cok_iyi": 170},
    8: {"dusuk": 110, "orta": 130, "iyi": 160, "cok_iyi": 180},
}


# ─── CLAUDE AI ANALİZ FONKSİYONU ─────────────────────────────────────────────

def analyze_reading_with_claude(transcription: str, original_text: str, student_name: str, student_grade: int, reading_duration_note: str = "") -> str:
    """
    Claude API ile öğrencinin okumasını analiz eder.
    Öğretmenin yazdığı transkript ile orijinal metni karşılaştırır.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        except Exception:
            pass
    
    if not api_key:
        return "❌ **HATA:** Claude API anahtarı bulunamadı. Lütfen ANTHROPIC_API_KEY ortam değişkenini ayarlayın."
    
    model = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")
    normlar = SINIF_NORMLARI.get(student_grade, SINIF_NORMLARI[4])
    
    # Hata kategorileri string
    kategoriler_str = "\n".join([
        f"{k['id']}. {k['emoji']} {k['ad']}: {k['aciklama']}" for k in HATA_KATEGORILERI
    ])
    
    system_prompt = f"""Sen, Türkiye'de ilkokul ve ortaokul düzeyinde öğrencilerin okuma becerilerini analiz eden uzman bir eğitim psikoloğu ve okuma uzmanısın. 

Görevin:
1. Öğretmenin yazdığı transkripsiyon (öğrencinin sesli okuduğu metin) ile orijinal metni karşılaştır
2. 10 hata kategorisinde detaylı analiz yap
3. En az 2000 kelimelik kapsamlı bir rapor üret

HATA KATEGORİLERİ:
{kategoriler_str}

SINIF NORMLARI ({student_grade}. Sınıf - Kelime/Dakika):
- Düşük: {normlar['dusuk']} k/dk altı
- Orta: {normlar['orta']} k/dk
- İyi: {normlar['iyi']} k/dk
- Çok İyi: {normlar['cok_iyi']} k/dk üstü

Raporunu Türkçe yaz, Markdown formatında, tablolar ve emojiler kullan.
Rapor profesyonel, empatik ve yapıcı olmalı."""

    duration_info = f"\n- **Okuma Süresi Notu:** {reading_duration_note}" if reading_duration_note else ""

    user_prompt = f"""## Öğrenci Bilgileri
- **Öğrenci:** {student_name}
- **Sınıf:** {student_grade}. Sınıf{duration_info}

## Orijinal Metin (Öğrencinin okuması gereken metin)
{original_text}

## Öğrencinin Okuduğu Metin (Öğretmen Transkripti)
{transcription}

## Görev
Yukarıda öğretmenin yazdığı transkripsiyon ile orijinal metni karşılaştırarak kapsamlı bir okuma hata analizi raporu üret.

### RAPOR YAPISI (Bu başlıkların hepsini kullan):

1. **📋 GENEL BİLGİLER** — Öğrenci adı, sınıf, tarih, metin bilgisi
2. **📝 TRANSKRİPSİYON** — Öğrencinin okuduğu metnin tam dökümü (öğretmenin yazdığı gibi)
3. **🔍 METİN KARŞILAŞTIRMASI** — Orijinal metin ile okunan metin arasındaki farklar (tablo halinde)
4. **📊 HATA ANALİZİ TABLOSU** — 10 kategori, her birinde bulunan hata sayısı (tablo)
5. **🔤 HARF HATALARI DETAYI** — Her harf hatasının detaylı açıklaması
6. **📎 HECE HATALARI DETAYI** — Her hece hatasının detaylı açıklaması
7. **❌ KELİME HATALARI DETAYI** — Her kelime hatasının detaylı açıklaması
8. **⏭️ ATLAMA HATALARI DETAYI** — Atlanan kelime/satırlar
9. **➕ EKLEME HATALARI DETAYI** — Eklenen kelimeler
10. **🔁 TEKRAR HATALARI DETAYI** — Tekrarlanan kelimeler
11. **🔄 TERS ÇEVİRME HATALARI DETAYI** — Ters çevrilen harf/heceler
12. **💨 NEFES/DURAK HATALARI DETAYI** — Yanlış yerlerde yapılan duraklar (transkriptte "..." veya parantez içi notlardan çıkar)
13. **🎵 VURGU/TONLAMA ANALİZİ** — Prozodi, tonlama, vurgu değerlendirmesi (transkriptteki notlara göre)
14. **⏱️ HIZ DEĞERLENDİRMESİ** — Kelime/dakika tahmini, sınıf normlarıyla karşılaştırma
15. **📈 OKUMA PROFİLİ** — Akıcılık, prozodi, özgüven, dikkat değerlendirmesi (her biri 1-10 puan)
16. **💪 GÜÇLÜ YÖNLER** — En az 3 madde
17. **🎯 GELİŞİM ALANLARI** — En az 3 madde
18. **👨‍🎓 ÖĞRENCİ İÇİN ÖNERİLER** — En az 5 madde
19. **👨‍👩‍👧 AİLE İÇİN ÖNERİLER** — En az 4 madde
20. **👩‍🏫 ÖĞRETMEN İÇİN ÖNERİLER** — En az 4 madde
21. **📅 GÜNLÜK/HAFTALIK EGZERSİZ PLANI** — Detaylı plan
22. **⚠️ UYARI NOTLARI** — Profesyonel değerlendirme gerektiren bulgular (varsa)

Her hata detayında şu formatı kullan:
| Orijinal | Okunan | Açıklama |
|----------|--------|----------|

Rapor en az 2000 kelime olmalı. Detaylı, kapsamlı ve yapıcı yaz."""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model=model,
            max_tokens=8192,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
        )
        
        # Yanıtı birleştir
        result_text = ""
        for block in message.content:
            if hasattr(block, 'text'):
                result_text += block.text
        
        return result_text if result_text else "❌ Claude API'den boş yanıt alındı."
        
    except anthropic.APIError as e:
        return f"❌ **Claude API Hatası:** {str(e)}"
    except Exception as e:
        return f"❌ **Beklenmeyen Hata:** {str(e)}"


def get_text_for_grade(grade: int) -> dict:
    """Sınıf düzeyine uygun metni döndürür."""
    return SINIF_METINLERI.get(grade, SINIF_METINLERI[4])

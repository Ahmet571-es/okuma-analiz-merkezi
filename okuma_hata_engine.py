# ============================================================
# okuma_hata_engine.py — Okuma Hata Analizi Motoru v1.0
# Sesli okuma kayıt → AI transkripsiyon → Hata kategorileme
# 1-8. Sınıf düzeyine göre metinler
# ============================================================

import json
import os
from datetime import datetime

# ============================================================
# HATA KATEGORİLERİ
# ============================================================
HATA_KATEGORILERI = {
    "harf_hatasi": {
        "name": "Harf Hatası",
        "icon": "🔤",
        "description": "Kelimedeki harflerin yanlış okunması (ör: 'bal' yerine 'bol')",
        "severity": 2,
    },
    "hece_hatasi": {
        "name": "Hece Hatası",
        "icon": "📎",
        "description": "Hecelerin yanlış bölünmesi veya okunması",
        "severity": 2,
    },
    "kelime_hatasi": {
        "name": "Kelime Hatası / Yanlış Okuma",
        "icon": "❌",
        "description": "Kelimenin tamamen farklı bir kelime olarak okunması",
        "severity": 3,
    },
    "atlama_hatasi": {
        "name": "Atlama Hatası",
        "icon": "⏭️",
        "description": "Kelime, satır veya bölüm atlanması",
        "severity": 3,
    },
    "ekleme_hatasi": {
        "name": "Ekleme Hatası",
        "icon": "➕",
        "description": "Metinde olmayan kelime veya eklerin eklenmesi",
        "severity": 2,
    },
    "tekrar_hatasi": {
        "name": "Tekrar Hatası",
        "icon": "🔁",
        "description": "Kelime veya cümlelerin gereksiz yere tekrarlanması",
        "severity": 1,
    },
    "ters_cevirme_hatasi": {
        "name": "Ters Çevirme Hatası",
        "icon": "🔄",
        "description": "Harflerin veya hecelerin yer değiştirmesi (ör: 'kapı' yerine 'pakı')",
        "severity": 3,
    },
    "nefes_hatasi": {
        "name": "Nefes / Durak Hatası",
        "icon": "💨",
        "description": "Yanlış yerde nefes alma, kelime ortasında durma",
        "severity": 1,
    },
    "vurgu_tonlama_hatasi": {
        "name": "Vurgu ve Tonlama Hatası",
        "icon": "🎵",
        "description": "Yanlış vurgu, monoton okuma, cümle melodisini yakalayamama",
        "severity": 1,
    },
    "hiz_hatasi": {
        "name": "Hız Hatası",
        "icon": "⏱️",
        "description": "Aşırı yavaş veya aşırı hızlı okuma",
        "severity": 1,
    },
}

# ============================================================
# SINIF BAZLI OKUMA HIZI NORMLARI (Kelime/Dakika)
# ============================================================
OKUMA_HIZI_NORMLARI = {
    1: {"cok_yavas": 20, "yavas": 35, "ortalama": 55, "hizli": 75, "cok_hizli": 95},
    2: {"cok_yavas": 40, "yavas": 60, "ortalama": 80, "hizli": 100, "cok_hizli": 120},
    3: {"cok_yavas": 60, "yavas": 80, "ortalama": 105, "hizli": 130, "cok_hizli": 155},
    4: {"cok_yavas": 80, "yavas": 100, "ortalama": 130, "hizli": 160, "cok_hizli": 185},
    5: {"cok_yavas": 90, "yavas": 115, "ortalama": 145, "hizli": 175, "cok_hizli": 210},
    6: {"cok_yavas": 100, "yavas": 130, "ortalama": 160, "hizli": 195, "cok_hizli": 230},
    7: {"cok_yavas": 110, "yavas": 140, "ortalama": 175, "hizli": 210, "cok_hizli": 250},
    8: {"cok_yavas": 120, "yavas": 150, "ortalama": 190, "hizli": 230, "cok_hizli": 270},
}

# ============================================================
# SINIF BAZLI OKUMA METİNLERİ (1-8. Sınıf)
# Her sınıf için metin uzunluğu doğru orantılı
# ============================================================
OKUMA_METINLERI = {
    1: {
        "id": "sinif1_m1",
        "title": "Küçük Kedi",
        "text": (
            "Bir küçük kedi vardı. Kedinin adı Pamuk'tu. Pamuk beyaz ve yumuşacıktı. "
            "Her sabah bahçeye çıkardı. Çiçeklerin arasında oynardı. Kelebeklerle koşardı. "
            "Akşam olunca eve gelirdi. Sıcak sütünü içerdi. Sonra yatağına kıvrılırdı. "
            "Pamuk çok mutlu bir kediydi."
        ),
        "kelime_sayisi": 42,
    },
    2: {
        "id": "sinif2_m1",
        "title": "Yağmurlu Gün",
        "text": (
            "Bugün hava çok yağmurluydu. Ayşe pencereden dışarı baktı. Yağmur damlaları cama "
            "çarpıyordu. Ayşe yağmurluğunu ve çizmelerini giydi. Dışarı çıktı. Su birikintilerinin "
            "içinde zıpladı. Ayakkabıları ıslandı ama çok eğlendi.\n\n"
            "Eve döndüğünde annesi ona sıcak bir çorba hazırlamıştı. Ayşe çorbasını içerken "
            "yağmurun sesini dinledi. Bu güzel bir gündü."
        ),
        "kelime_sayisi": 62,
    },
    3: {
        "id": "sinif3_m1",
        "title": "Orman Gezisi",
        "text": (
            "Geçen hafta sonu ailemle birlikte ormana gittik. Sabah erkenden yola çıktık. "
            "Arabada şarkılar söyledik. Ormana vardığımızda hava çok güzeldi. Kuşlar "
            "ötüyor, rüzgâr yaprakları sallıyordu.\n\n"
            "Babam bize farklı ağaç türlerini gösterdi. Çam ağaçlarının yaprakları "
            "iğne gibiydi. Meşe ağaçlarının yaprakları ise geniş ve yeşildi. Annem "
            "bizimle birlikte çiçek topladı. Kardeşim ise böcekleri inceledi.\n\n"
            "Öğle yemeğini ağaçların altında yedik. Sandviçlerimiz çok lezzetliydi. "
            "Akşam eve dönerken hepimiz çok yorgun ama çok mutluyduk."
        ),
        "kelime_sayisi": 98,
    },
    4: {
        "id": "sinif4_m1",
        "title": "Kütüphane Macerası",
        "text": (
            "Elif okumayı çok seven bir kızdı. Her hafta sonu mahalle kütüphanesine "
            "giderdi. Kütüphaneci Mehmet Bey onu her gördüğünde gülümserdi. Elif'in "
            "en sevdiği köşe, pencerenin yanındaki rahat koltuktu. Oraya oturur ve "
            "saatlerce kitap okurdu.\n\n"
            "Bir gün Elif kütüphanede eski bir harita buldu. Harita, mahalledeki parkın "
            "altında gizli bir tünel olduğunu gösteriyordu. Elif çok heyecanlandı. "
            "En yakın arkadaşı Mert'i aradı ve planlarını anlattı. İkisi birlikte "
            "parka gittiler.\n\n"
            "Parkta büyük meşe ağacının yanında küçük bir kapak buldular. Kapağı "
            "açtıklarında merdivenler gördüler. Aşağı indiklerinde eski bir kütüphane "
            "daha vardı. Duvarlar kitaplarla kaplıydı. Bu, yüz yıl önce kapatılmış "
            "eski bir okuma odasıydı. Elif ve Mert çok şaşırdılar."
        ),
        "kelime_sayisi": 137,
    },
    5: {
        "id": "sinif5_m1",
        "title": "Doğanın Dört Mevsimi",
        "text": (
            "Dünyamız güneşin etrafında dönerken dört farklı mevsim yaşanır. Her mevsimin "
            "kendine özgü güzellikleri ve özellikleri vardır. İlkbahar, doğanın uyanış "
            "mevsimidir. Ağaçlar çiçek açar, kuşlar göç ettikleri yerlerden geri döner "
            "ve günler uzamaya başlar. Çiftçiler tarlalarını ekmeye hazırlanır.\n\n"
            "Yaz mevsiminde sıcaklıklar artar ve güneş en uzun süre gökyüzünde kalır. "
            "İnsanlar tatile gider, denizde yüzer ve açık havada vakit geçirir. Meyveler "
            "ve sebzeler bollaşır. Karpuz, kavun ve şeftali gibi meyveler sofraları süsler.\n\n"
            "Sonbahar geldiğinde yapraklar renk değiştirir. Sarı, turuncu ve kırmızı tonları "
            "doğayı bir tabloya dönüştürür. Göçmen kuşlar sıcak bölgelere doğru yola çıkar. "
            "Çiftçiler hasatlarını toplar ve kışa hazırlık yapar.\n\n"
            "Kış mevsiminde ise doğa beyaz bir örtüyle kaplanır. Sıcaklıklar düşer ve kar "
            "yağar. Bazı hayvanlar kış uykusuna yatar. İnsanlar kalın giysiler giyer, sıcak "
            "içecekler içer ve şöminenin başında vakit geçirir."
        ),
        "kelime_sayisi": 172,
    },
    6: {
        "id": "sinif6_m1",
        "title": "Suyun Yolculuğu",
        "text": (
            "Su, yaşamın en temel kaynağıdır ve doğada sürekli bir döngü içinde hareket eder. "
            "Bu döngüye 'su döngüsü' adı verilir. Güneşin ısıttığı deniz, göl ve nehir "
            "yüzeylerinden su buharlaşarak atmosfere yükselir. Bu buharlaşma, gözle görülemeyecek "
            "kadar küçük su moleküllerinin gaz haline dönüşmesidir.\n\n"
            "Atmosfere yükselen su buharı soğuyarak küçük su damlacıklarına veya buz kristallerine "
            "dönüşür. Bu damlacıklar bir araya gelerek bulutları oluşturur. Yoğunlaşma olarak "
            "adlandırılan bu süreç, bulutların oluşumunun temelini oluşturur. Bulutlar rüzgârla "
            "birlikte taşınarak farklı bölgelere ulaşır.\n\n"
            "Bulutlardaki su damlacıkları yeterince büyüdüğünde yağmur, kar veya dolu olarak "
            "yeryüzüne düşer. Bu yağışlar toprağa, nehirlere ve göllere ulaşır. Bir kısmı "
            "yeraltına sızarak yeraltı su kaynaklarını besler. Bir kısmı ise akarsular aracılığıyla "
            "tekrar denizlere ve okyanuslara ulaşır.\n\n"
            "Su döngüsü milyarlarca yıldır kesintisiz devam etmektedir. Bugün içtiğimiz su, "
            "belki de milyonlarca yıl önce bir dinozorun içtiği suyla aynıdır. Bu düşünce, "
            "suyun ne kadar değerli ve korunması gereken bir kaynak olduğunu göstermektedir."
        ),
        "kelime_sayisi": 193,
    },
    7: {
        "id": "sinif7_m1",
        "title": "Dijital Çağda İletişim",
        "text": (
            "İnsanlık tarihi boyunca iletişim yöntemleri sürekli değişim göstermiştir. "
            "İlk insanlar mağara duvarlarına resimler çizerek mesajlarını iletirken, daha "
            "sonra yazının icadıyla birlikte düşünceler kalıcı hale getirilmeye başlanmıştır. "
            "Matbaanın keşfi bilginin kitlesel yayılmasını sağlamış, telgraf ve telefon ise "
            "uzak mesafeler arasındaki iletişimi mümkün kılmıştır.\n\n"
            "Günümüzde internet ve akıllı telefonlar, iletişimi tamamen yeni bir boyuta "
            "taşımıştır. Sosyal medya platformları aracılığıyla dünyanın herhangi bir "
            "yerindeki insanla anlık olarak bağlantı kurmak mümkün hale gelmiştir. Video "
            "görüşmeleri, sesli mesajlar ve anlık ileti uygulamaları günlük yaşamımızın "
            "vazgeçilmez parçaları olmuştur.\n\n"
            "Ancak dijital iletişimin bazı olumsuz yönleri de bulunmaktadır. Yüz yüze "
            "iletişimin yerini ekranlar almaya başlamıştır. İnsanlar aynı odada otururken "
            "bile telefonlarıyla meşgul olabilmektedir. Bu durum, kişiler arası ilişkilerin "
            "yüzeyselleşmesine ve empati becerisinin azalmasına yol açabilmektedir.\n\n"
            "Ayrıca dijital ortamda paylaşılan bilgilerin doğruluğu her zaman güvenilir "
            "değildir. Yanlış bilgi ve söylentiler sosyal medyada hızla yayılabilmektedir. "
            "Bu nedenle eleştirel düşünme becerisi ve medya okuryazarlığı günümüzde "
            "her zamankinden daha önemli hale gelmiştir. Bilgiyi sorgulamak, kaynağını "
            "araştırmak ve farklı bakış açılarını değerlendirmek dijital çağın "
            "olmazsa olmaz becerileridir."
        ),
        "kelime_sayisi": 215,
    },
    8: {
        "id": "sinif8_m1",
        "title": "Bilimin Işığında Keşifler",
        "text": (
            "Bilim insanlığın en güçlü aracıdır. Tarih boyunca merak duygusunun "
            "peşinden giden bilim insanları, doğanın sırlarını çözerek uygarlığın "
            "ilerlemesini sağlamışlardır. Antik Yunan'da Aristoteles'in gözlemleri, "
            "Orta Çağ'da İbn-i Sina'nın tıp çalışmaları ve Rönesans döneminde "
            "Kopernik'in güneş merkezli evren modeli, bilimsel düşüncenin kilometre "
            "taşlarıdır.\n\n"
            "On yedinci yüzyılda Newton'un hareket yasaları ve yerçekimi kuramı, "
            "fizik biliminin temellerini oluşturmuştur. Bu buluşlar sayesinde "
            "gezegenlerin hareketlerinden köprülerin inşasına kadar pek çok alanda "
            "ilerleme kaydedilmiştir. On dokuzuncu yüzyılda Darwin'in evrim teorisi "
            "canlıların çeşitliliğini açıklarken, Pasteur'ün mikrop teorisi modern "
            "tıbbın doğmasına öncülük etmiştir.\n\n"
            "Yirminci yüzyıl ise bilimsel devrimin en hızlı yaşandığı dönem olmuştur. "
            "Einstein'ın görelilik teorisi uzay ve zamanın doğası hakkındaki anlayışımızı "
            "kökten değiştirmiştir. Kuantum fiziğinin gelişmesi atom altı dünyanın "
            "gizemli kurallarını ortaya koymuştur. DNA'nın keşfi genetik biliminin "
            "kapılarını aralamış ve bugün genetik mühendisliği, kişiselleştirilmiş tıp "
            "gibi alanlarda devrim niteliğinde ilerlemeler yaşanmaktadır.\n\n"
            "Bilimin temel ilkesi sorgulamaktır. Her yeni keşif, daha önce bilinmeyen "
            "sorular ortaya çıkarmıştır. Evrenin genişlediği, kara deliklerin var "
            "olduğu, beynin plastisitesi gibi bulgular göstermektedir ki bilim "
            "sonsuz bir keşif yolculuğudur. Bu yolculukta merak, şüphecilik ve "
            "kanıta dayalı düşünme bizim en değerli rehberlerimizdir.\n\n"
            "Günümüzde yapay zekâ, kuantum bilgisayarlar ve uzay keşifleri gibi alanlar "
            "bilimin sınırlarını sürekli genişletmektedir. Gelecek nesiller, bugünün "
            "hayal bile edemediğimiz keşiflerini yapacaktır."
        ),
        "kelime_sayisi": 256,
    },
}


def get_metin_for_grade(grade):
    """Sınıf düzeyine uygun metni döndürür."""
    grade = max(1, min(8, grade))
    return OKUMA_METINLERI[grade]


def count_words(text):
    """Metindeki kelime sayısını hesaplar."""
    clean = text.replace("\n", " ").strip()
    return len(clean.split())


def classify_reading_speed(wpm, grade):
    """Okuma hızını sınıflandırır."""
    norms = OKUMA_HIZI_NORMLARI.get(grade, OKUMA_HIZI_NORMLARI[4])
    if wpm < norms["cok_yavas"]:
        return "cok_yavas", "Çok Yavaş", "🔴"
    elif wpm < norms["yavas"]:
        return "yavas", "Yavaş", "🟠"
    elif wpm < norms["hizli"]:
        return "ortalama", "Ortalama", "🟡"
    elif wpm < norms["cok_hizli"]:
        return "hizli", "Hızlı", "🔵"
    else:
        return "cok_hizli", "Çok Hızlı", "🟢"


# ============================================================
# AI ANALİZ PROMPT'U — CLAUDE İLE OKUMA HATASI ANALİZİ
# ============================================================

def build_okuma_hata_prompt(original_text, transcription, grade, student_name="", student_age=None, reading_time_seconds=None):
    """Claude AI için okuma hata analizi prompt'u oluşturur."""

    word_count = count_words(original_text)
    wpm = None
    speed_info = ""
    if reading_time_seconds and reading_time_seconds > 0:
        wpm = round(word_count / (reading_time_seconds / 60))
        speed_key, speed_label, speed_emoji = classify_reading_speed(wpm, grade)
        norms = OKUMA_HIZI_NORMLARI.get(grade, OKUMA_HIZI_NORMLARI[4])
        speed_info = f"""
### OKUMA HIZI BİLGİSİ
- Toplam kelime: {word_count}
- Okuma süresi: {round(reading_time_seconds, 1)} saniye ({round(reading_time_seconds/60, 2)} dakika)
- Okuma hızı: {wpm} kelime/dakika
- Değerlendirme: {speed_emoji} {speed_label}
- {grade}. Sınıf Normları: Çok Yavaş (<{norms['cok_yavas']}), Yavaş ({norms['cok_yavas']}-{norms['yavas']}), Ortalama ({norms['yavas']}-{norms['hizli']}), Hızlı ({norms['hizli']}-{norms['cok_hizli']}), Çok Hızlı (>{norms['cok_hizli']})
"""

    student_info = ""
    if student_name:
        student_info = f"- Öğrenci: {student_name}\n"
    if student_age:
        student_info += f"- Yaş: {student_age}\n"

    return f"""# ROL VE GÖREVİN

Sen, Türkiye'nin en deneyimli okuma uzmanlarından birisin. 20 yıllık okuma eğitimi ve okuma güçlüğü tanılama deneyimine sahip bir klinik eğitim uzmanısın.

Görevin: Bir öğrencinin sesli okumasının transkripsiyonunu orijinal metinle karşılaştırarak kapsamlı bir okuma hata analizi raporu üretmek.

---

# ÖĞRENCİ BİLGİLERİ
{student_info}- Sınıf: {grade}. Sınıf
- Metin kelime sayısı: {word_count}
{speed_info}

---

# ORİJİNAL METİN (Öğrencinin okuması gereken metin)
```
{original_text}
```

---

# ÖĞRENCİNİN OKUDUĞU METİN (Ses kaydının transkripsiyonu)
```
{transcription}
```

---

# ANALİZ TALİMATLARI

## 1. KELIME KELIME KARŞILAŞTIRMA
Orijinal metindeki her kelimeyi, öğrencinin okuduğu metinle tek tek karşılaştır.
Her farklılığı tespit et ve aşağıdaki hata kategorilerine göre sınıflandır:

### HATA KATEGORİLERİ:

1. **🔤 Harf Hatası**: Kelimedeki bir veya birkaç harfin yanlış okunması
   - Örnek: "balık" yerine "bolık", "gelen" yerine "gelen"
   
2. **📎 Hece Hatası**: Hecelerin yanlış bölünmesi veya okunması
   - Örnek: "ka-pı" yerine "kap-ı", heceleri yanlış ayırma

3. **❌ Kelime Hatası / Yanlış Okuma**: Kelimenin tamamen farklı okunması
   - Örnek: "güneş" yerine "gündüz", "okul" yerine "kitap"

4. **⏭️ Atlama Hatası**: Kelime, satır veya bölüm atlanması
   - Metinde olan ama öğrencinin okumadığı kısımlar

5. **➕ Ekleme Hatası**: Metinde olmayan kelime eklenmesi
   - Öğrencinin metinde olmayan kelimeleri eklemesi

6. **🔁 Tekrar Hatası**: Kelime veya ifadelerin gereksiz tekrarlanması
   - Aynı kelimeyi veya cümleyi tekrar okuma

7. **🔄 Ters Çevirme Hatası**: Harf veya hece sırasının değiştirilmesi
   - Örnek: "kapı" yerine "pakı", "ev" yerine "ve"

8. **💨 Nefes / Durak Hatası**: Yanlış yerde durma, kelime ortasında bölme
   - Cümlenin ortasında anlamsız durma, kelimeyi bölerek okuma

9. **🎵 Vurgu ve Tonlama Hatası**: Yanlış vurgu, monoton okuma
   - Soru cümlesini düz okuma, vurguyu yanlış yere koyma

10. **⏱️ Hız Hatası**: Çok yavaş veya çok hızlı okuma (hız bilgisinden değerlendir)

---

## 2. YANIT FORMATI

Yanıtını MUTLAKA aşağıdaki JSON formatında ver. Başka hiçbir metin ekleme, SADECE JSON döndür:

```json
{{
  "ozet": {{
    "toplam_kelime": {word_count},
    "dogru_okunan": <sayı>,
    "toplam_hata": <sayı>,
    "dogruluk_yuzdesi": <yüzde>,
    "okuma_hizi_wpm": {wpm if wpm else "null"},
    "genel_duzey": "<Çok İyi / İyi / Orta / Zayıf / Çok Zayıf>",
    "genel_duzey_emoji": "<🟢/🔵/🟡/🟠/🔴>"
  }},
  "hata_dagilimi": {{
    "harf_hatasi": <sayı>,
    "hece_hatasi": <sayı>,
    "kelime_hatasi": <sayı>,
    "atlama_hatasi": <sayı>,
    "ekleme_hatasi": <sayı>,
    "tekrar_hatasi": <sayı>,
    "ters_cevirme_hatasi": <sayı>,
    "nefes_hatasi": <sayı>,
    "vurgu_tonlama_hatasi": <sayı>,
    "hiz_hatasi": <sayı>
  }},
  "hata_detaylari": [
    {{
      "kategori": "<hata_kategorisi_key>",
      "orijinal": "<orijinal kelime/ifade>",
      "okunan": "<öğrencinin okuduğu>",
      "aciklama": "<kısa açıklama>",
      "konum": "<metindeki yaklaşık konum (başlangıç/orta/son)>"
    }}
  ],
  "okuma_profili": {{
    "akicilik": "<Akıcı / Kısmen Akıcı / Takılmalı / Heceleyerek>",
    "prozodi": "<İyi / Orta / Zayıf>",
    "ozguven": "<Yüksek / Orta / Düşük>",
    "dikkat": "<İyi / Orta / Zayıf>"
  }},
  "guclu_yonler": [
    "<öğrencinin okumada güçlü olduğu noktalar — en az 3 madde>"
  ],
  "gelisim_alanlari": [
    "<öğrencinin geliştirmesi gereken alanlar — en az 3 madde>"
  ],
  "oneriler": {{
    "ogrenci_icin": [
      "<öğrenciye özel somut öneriler — en az 5 madde>"
    ],
    "aile_icin": [
      "<aileye özel somut öneriler — en az 4 madde>"
    ],
    "ogretmen_icin": [
      "<öğretmene özel somut öneriler — en az 4 madde>"
    ]
  }},
  "egzersiz_plani": {{
    "gunluk": "<günlük okuma egzersizi önerisi>",
    "haftalik": "<haftalık plan önerisi>",
    "hedef": "<1 ay sonrası için hedef>"
  }},
  "uyari_notlari": [
    "<varsa disleksi, dikkat eksikliği gibi profesyonel değerlendirme gerektiren bulgular — klinik tanı koymadan, sadece gözlem olarak>"
  ],
  "detayli_rapor": "<Markdown formatında, en az 1500 kelimelik kapsamlı ve profesyonel analiz raporu. Tüm bulguları, hata analizini, öğrenci profilini, önerileri ve egzersiz planını içermeli. Tablolar, emoji ve görsel unsurlar kullanılmalı. Rapor, bir eğitim psikoloğunun yazacağı kalitede olmalı.>"
}}
```

## 3. KRİTİK KURALLAR

1. **HER HATAYI TEK TEK BUL**: Orijinal metni kelime kelime tara, hiçbir hatayı atlama.
2. **DOĞRU KATEGORİZE ET**: Her hatayı doğru kategoriye ata. Bir hata birden fazla kategoriye girebiliyorsa en baskın olanı seç.
3. **SAYISAL DOĞRULUK**: Toplam hata sayısı ile hata dağılımındaki sayıların toplamı tutarlı olmalı.
4. **SINIF DÜZEYİ**: {grade}. sınıf düzeyindeki bir öğrencinin gelişimsel beklentilerini göz önünde bulundur.
5. **OLUMLU TON**: Rapor yapıcı ve güçlendirici olmalı. Öğrenciyi yargılama, potansiyelini vurgula.
6. **KLİNİK TANI KOYMA**: Disleksi, DEHB gibi klinik tanılar koyma. Sadece gözlem olarak not düş.
7. **DETAYLI RAPOR**: `detayli_rapor` alanı en az 1500 kelime, Markdown formatında, profesyonel ve kapsamlı olmalı.

SADECE JSON formatında yanıt ver. Başka hiçbir metin ekleme."""


def build_audio_transcription_prompt(original_text, grade):
    """Claude AI'a ses kaydını transkribe ettirmek için prompt."""
    return f"""Aşağıdaki ses kaydı, {grade}. sınıf düzeyinde bir Türk öğrencinin sesli okumasıdır.

Öğrencinin okuması gereken orijinal metin:
```
{original_text}
```

Lütfen ses kaydını DİKKATLİCE dinle ve öğrencinin GERÇEKTE ne söylediğini olduğu gibi transkribe et.

ÖNEMLİ KURALLAR:
1. Öğrencinin söylediğini AYNEN yaz — düzeltme yapma
2. Yanlış okunan kelimeleri yanlış haliyle yaz
3. Atlanan kelimeleri yazma (çünkü öğrenci onları söylemedi)
4. Eklenen kelimeleri yaz (çünkü öğrenci onları söyledi)
5. Tekrarlanan kelimeleri tekrar yazarak göster
6. Duraksamaları [...] ile göster
7. Anlaşılamayan kısımları [anlaşılamadı] ile göster

SADECE transkripsiyon metnini döndür, başka hiçbir şey ekleme."""


# ============================================================
# SONUÇ İŞLEME FONKSİYONLARI
# ============================================================

def parse_ai_response(ai_response_text):
    """Claude AI'ın JSON yanıtını parse eder."""
    try:
        # JSON bloğunu bul
        text = ai_response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        result = json.loads(text)
        return result, None
    except json.JSONDecodeError as e:
        # İkinci deneme: JSON'u regex ile bul
        import re
        json_match = re.search(r'\{[\s\S]*\}', ai_response_text)
        if json_match:
            try:
                result = json.loads(json_match.group())
                return result, None
            except:
                pass
        return None, f"JSON parse hatası: {e}"


def calculate_overall_score(analysis_result):
    """Analiz sonucundan genel skor hesaplar (0-100)."""
    if not analysis_result or "ozet" not in analysis_result:
        return 0

    ozet = analysis_result["ozet"]
    dogruluk = ozet.get("dogruluk_yuzdesi", 0)
    return round(dogruluk, 1)


def get_performance_level(score):
    """Genel skora göre performans düzeyini belirler."""
    if score >= 95:
        return "Mükemmel", "🟢", "Okuma becerilerin harika! Devam et!"
    elif score >= 85:
        return "Çok İyi", "🔵", "Okuma becerilerin güçlü, küçük iyileştirmelerle mükemmele ulaşabilirsin."
    elif score >= 70:
        return "İyi", "🟡", "İyi bir okuma performansı! Düzenli pratikle daha da gelişebilirsin."
    elif score >= 50:
        return "Gelişmekte", "🟠", "Okuma becerilerin gelişiyor. Düzenli egzersizlerle hızla ilerleme kaydedebilirsin."
    else:
        return "Destek Gerekli", "🔴", "Okuma becerilerinde destek ihtiyacı var. Endişelenme, doğru rehberlikle hızla gelişebilirsin!"


def generate_summary_report(analysis_result, grade, reading_time_seconds=None):
    """Analiz sonucundan özet rapor markdown'ı üretir."""
    if not analysis_result:
        return "Analiz sonucu bulunamadı."

    # detayli_rapor varsa onu döndür
    if "detayli_rapor" in analysis_result and analysis_result["detayli_rapor"]:
        return analysis_result["detayli_rapor"]

    # Yoksa basit özet oluştur
    ozet = analysis_result.get("ozet", {})
    hata_dag = analysis_result.get("hata_dagilimi", {})

    score = ozet.get("dogruluk_yuzdesi", 0)
    level, emoji, msg = get_performance_level(score)

    report = f"""# 📖 OKUMA HATA ANALİZİ RAPORU

## {emoji} Genel Değerlendirme: {level}

{msg}

---

## 📊 Özet Bilgiler

| Gösterge | Değer |
|----------|-------|
| Toplam Kelime | {ozet.get('toplam_kelime', '?')} |
| Doğru Okunan | {ozet.get('dogru_okunan', '?')} |
| Toplam Hata | {ozet.get('toplam_hata', '?')} |
| Doğruluk Oranı | %{score} |
| Okuma Hızı | {ozet.get('okuma_hizi_wpm', '?')} kel/dk |
| Sınıf Düzeyi | {grade}. Sınıf |

---

## 🔍 Hata Dağılımı

"""
    for key, info in HATA_KATEGORILERI.items():
        count = hata_dag.get(key, 0)
        if count > 0:
            report += f"- {info['icon']} **{info['name']}**: {count} hata\n"

    report += "\n---\n\n"

    # Güçlü yönler
    guclu = analysis_result.get("guclu_yonler", [])
    if guclu:
        report += "## 💪 Güçlü Yönler\n\n"
        for g in guclu:
            report += f"- ✅ {g}\n"
        report += "\n"

    # Gelişim alanları
    gelisim = analysis_result.get("gelisim_alanlari", [])
    if gelisim:
        report += "## 🌱 Gelişim Alanları\n\n"
        for g in gelisim:
            report += f"- 🎯 {g}\n"

    return report

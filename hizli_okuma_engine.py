# ============================================================
# hizli_okuma_engine.py — Hızlı Okuma + Anlama Testi
# GitHub'daki mevcut projeden adapte edilmiş (1-8. Sınıf)
# ============================================================

KADEME_MAP = {
    1: "kademe_1", 2: "kademe_1", 3: "kademe_1", 4: "kademe_1",
    5: "kademe_1", 6: "kademe_1",
    7: "kademe_2", 8: "kademe_2",
    9: "kademe_3", 10: "kademe_3",
    11: "kademe_4", 12: "kademe_4",
}

KADEME_LABELS = {
    "kademe_1": "1-6. Sınıf (Temel)",
    "kademe_2": "7-8. Sınıf (Orta)",
    "kademe_3": "9-10. Sınıf (İleri)",
    "kademe_4": "11-12. Sınıf (Üst)",
}

WPM_NORMS = {
    "kademe_1": {"cok_yavas": 40, "yavas": 60, "ortalama": 90, "hizli": 120, "cok_hizli": 150},
    "kademe_2": {"cok_yavas": 90, "yavas": 120, "ortalama": 155, "hizli": 190, "cok_hizli": 230},
    "kademe_3": {"cok_yavas": 120, "yavas": 155, "ortalama": 195, "hizli": 240, "cok_hizli": 280},
    "kademe_4": {"cok_yavas": 150, "yavas": 185, "ortalama": 230, "hizli": 275, "cok_hizli": 320},
}

def grade_to_kademe(grade):
    return KADEME_MAP.get(grade, "kademe_1")


# ============================================================
# METİNLER
# ============================================================
K1_PASSAGES = [
    {
        "id": "k1_p1",
        "title": "Deniz Kaplumbağalarının Yolculuğu",
        "text": (
            "Deniz kaplumbağaları, dünyanın en ilginç gezginlerinden biridir. Her yıl binlerce kilometre yüzerek "
            "doğdukları sahillere geri dönerler. Dişi kaplumbağalar yumurtalarını kumda açtıkları çukurlara bırakır "
            "ve üzerlerini kumla örter. Yaklaşık iki ay sonra yumurtadan çıkan minik yavrular, ay ışığının "
            "yansımasını takip ederek denize ulaşmaya çalışır. Ancak bu yolculuk oldukça tehlikelidir. Kuşlar, "
            "yengeçler ve diğer avcılar yavruları yakalamaya çalışır. Denize ulaşmayı başaran yavrulardan sadece "
            "binde biri yetişkin olabilir.\n\n"
            "Bilim insanları, deniz kaplumbağalarının dünyanın manyetik alanını kullanarak yollarını bulduğunu "
            "keşfetmiştir. Bu yetenek sayesinde okyanusun ortasında bile kaybolmadan binlerce kilometre yüzebilirler. "
            "Kaplumbağalar ayrıca denizanası, yosun ve küçük deniz canlılarıyla beslenir. Plastik poşetler "
            "denizanasına benzediği için kaplumbağalar bazen bunları yutarak hastalanır veya ölür.\n\n"
            "Bugün yedi deniz kaplumbağası türünden altısı nesli tehlike altında olan canlılar listesindedir. "
            "Sahillerdeki yapay ışıklar, yavruların deniz yerine karaya doğru yönelmesine neden olur. Plastik "
            "kirliliği, iklim değişikliği ve avlanma da kaplumbağaların hayatını tehdit etmektedir. Birçok ülke "
            "kaplumbağa yumurtlama sahillerini koruma altına almış ve gönüllü koruma programları başlatmıştır. "
            "Türkiye'de de Dalyan, Patara ve Anamur gibi sahiller önemli yumurtlama alanlarıdır."
        ),
        "questions": [
            {"id": "k1_q1", "text": "Dişi kaplumbağalar yumurtalarını nereye bırakır?", "options": {"a": "Denizin dibine", "b": "Kayaların arasına", "c": "Kumda açtıkları çukurlara", "d": "Ağaçların altına"}, "answer": "c"},
            {"id": "k1_q2", "text": "Yavrular denizi nasıl bulur?", "options": {"a": "Annelerini takip ederek", "b": "Ay ışığının yansımasını takip ederek", "c": "Koku alarak", "d": "Rüzgârı takip ederek"}, "answer": "b"},
            {"id": "k1_q3", "text": "Denize ulaşan yavrulardan ne kadarı yetişkin olabilir?", "options": {"a": "Yarısı", "b": "Onda biri", "c": "Binde biri", "d": "Hepsi"}, "answer": "c"},
            {"id": "k1_q4", "text": "Kaplumbağalar yollarını nasıl bulur?", "options": {"a": "Yıldızlara bakarak", "b": "Dünyanın manyetik alanını kullanarak", "c": "Akıntıları takip ederek", "d": "Diğer kaplumbağaları izleyerek"}, "answer": "b"},
            {"id": "k1_q5", "text": "Plastik poşetler neden tehlikelidir?", "options": {"a": "Gürültü çıkardığı için", "b": "Sıcaklığı değiştirdiği için", "c": "Denizanasına benzediği için yutarlar", "d": "Yüzmelerini engellediği için"}, "answer": "c"},
            {"id": "k1_q6", "text": "Kaç tür nesli tehlike altındadır?", "options": {"a": "Üç", "b": "Dört", "c": "Beş", "d": "Altı"}, "answer": "d"},
            {"id": "k1_q7", "text": "Yapay ışıklar yavruları nasıl etkiler?", "options": {"a": "Büyümelerini sağlar", "b": "Deniz yerine karaya yönelmelerine neden olur", "c": "Erken çıkmalarına neden olur", "d": "Etkilemez"}, "answer": "b"},
            {"id": "k1_q8", "text": "Türkiye'deki yumurtlama sahillerinden biri hangisidir?", "options": {"a": "Kızkumu", "b": "Dalyan", "c": "Ölüdeniz", "d": "Çeşme"}, "answer": "b"},
            {"id": "k1_q9", "text": "Metnin ana düşüncesi nedir?", "options": {"a": "Kaplumbağalar çok hızlı yüzer", "b": "Deniz kaplumbağaları ilginç canlılardır ve korunmaya ihtiyaçları vardır", "c": "Türkiye'nin sahilleri güzeldir", "d": "Plastik poşetler yasaklanmalıdır"}, "answer": "b"},
            {"id": "k1_q10", "text": "Yumurtalar ne kadar sürede yavruya dönüşür?", "options": {"a": "Bir hafta", "b": "İki hafta", "c": "Bir ay", "d": "İki ay"}, "answer": "d"},
        ],
    },
]

K2_PASSAGES = [
    {
        "id": "k2_p1",
        "title": "Yapay Zekâ ve Geleceğimiz",
        "text": (
            "Yapay zekâ, son yılların en çok konuşulan teknolojik gelişmesidir. Bilgisayarların insan gibi "
            "düşünmesi, öğrenmesi ve karar vermesi anlamına gelen bu kavram, hayatımızın birçok alanına girmiştir. "
            "Telefonlarımızdaki sesli asistanlar, sosyal medyadaki öneri algoritmaları ve otomobillerdeki sürücü "
            "destek sistemleri yapay zekânın günlük hayattaki örneklerindendir.\n\n"
            "Yapay zekânın temelinde makine öğrenmesi adı verilen bir yöntem bulunur. Bu yöntemde bilgisayarlara "
            "büyük miktarda veri verilir ve bilgisayar bu verilerden kalıplar çıkararak kendi kendine öğrenir. "
            "Örneğin bir yapay zekâya milyonlarca kedi fotoğrafı gösterildiğinde, bir süre sonra daha önce hiç "
            "görmediği bir kedi fotoğrafını tanıyabilir hâle gelir.\n\n"
            "Tıp alanında yapay zekâ büyük bir devrim yaratmaktadır. Röntgen ve MR görüntülerini analiz ederek "
            "hastalıkları doktorlardan daha erken tespit edebilen sistemler geliştirilmiştir. Eğitim alanında "
            "ise her öğrencinin seviyesine göre özelleştirilmiş ders içerikleri sunan akıllı sistemler "
            "kullanılmaya başlanmıştır.\n\n"
            "Ancak yapay zekânın bazı riskleri de bulunmaktadır. İş gücü piyasasında birçok mesleğin ortadan "
            "kalkacağı öngörülmektedir. Uzmanlar, yapay zekânın insanların yerini almayacağını, aksine onlarla "
            "birlikte çalışacağını düşünmektedir. Bu nedenle eleştirel düşünme, yaratıcılık ve duygusal zekâ "
            "gibi insana özgü becerilerin önemi daha da artacaktır."
        ),
        "questions": [
            {"id": "k2_q1", "text": "Makine öğrenmesi nasıl çalışır?", "options": {"a": "Tek tek kurallar yazılır", "b": "Büyük verilerden kalıplar çıkararak kendi kendine öğrenir", "c": "İnsan beyni bağlanır", "d": "Bilgisayarlar birbirleriyle konuşur"}, "answer": "b"},
            {"id": "k2_q2", "text": "Tıpta yapay zekânın katkısı nedir?", "options": {"a": "Ameliyat yapmak", "b": "Hastalıkları erken tespit etmek", "c": "Doktorların yerini almak", "d": "Hastane yönetimi"}, "answer": "b"},
            {"id": "k2_q3", "text": "AI tarafından devralınamayacak iş hangisidir?", "options": {"a": "Veri girişi", "b": "Fabrika işçiliği", "c": "Yaratıcı sanat", "d": "Çeviri"}, "answer": "c"},
            {"id": "k2_q4", "text": "Gelecekte en başarılı olacaklar kimlerdir?", "options": {"a": "En hızlı yazabilenler", "b": "Yapay zekâyı etkili kullanabilenler", "c": "En çok dil bilenler", "d": "Robotlardan kaçınanlar"}, "answer": "b"},
            {"id": "k2_q5", "text": "Eğitimde AI nasıl kullanılır?", "options": {"a": "Maaş hesaplamak", "b": "Öğrenciye özel ders içerikleri sunmak", "c": "Sınav sızdırmak", "d": "Notları yükseltmek"}, "answer": "b"},
            {"id": "k2_q6", "text": "AI'ın öğrenmesi insandan nasıl farklıdır?", "options": {"a": "Daha yavaş", "b": "Hiç farklı değil", "c": "Daha az doğru", "d": "Çok daha hızlı"}, "answer": "d"},
            {"id": "k2_q7", "text": "Günlük yaşamda AI örneği nedir?", "options": {"a": "Kalem", "b": "Sesli asistan", "c": "Bisiklet", "d": "Kitap"}, "answer": "b"},
            {"id": "k2_q8", "text": "Metnin son paragrafındaki mesaj nedir?", "options": {"a": "AI tehlikelidir", "b": "Herkes programlama öğrenmeli", "c": "İnsana özgü becerilerin önemi artacak", "d": "AI yasaklanmalı"}, "answer": "c"},
            {"id": "k2_q9", "text": "AI risklerinden biri nedir?", "options": {"a": "Elektrik kesilmesi", "b": "Bazı mesleklerin ortadan kalkması", "c": "Havanın kirlenmesi", "d": "Kitapların yok olması"}, "answer": "b"},
            {"id": "k2_q10", "text": "AI bir kedi fotoğrafını nasıl tanır?", "options": {"a": "Birisi söyler", "b": "Milyonlarca fotoğraftan kalıplar öğrenerek", "c": "Kedi sesini duyar", "d": "İnternetten bakar"}, "answer": "b"},
        ],
    },
]

ALL_PASSAGES = {
    "kademe_1": K1_PASSAGES,
    "kademe_2": K2_PASSAGES,
}


# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================

def count_words(text):
    return len(text.split())

def get_passage_for_grade(grade):
    kademe = grade_to_kademe(grade)
    passages = ALL_PASSAGES.get(kademe, K1_PASSAGES)
    return passages[0], kademe

def get_wpm_norms(kademe):
    return WPM_NORMS.get(kademe, WPM_NORMS["kademe_1"])

def classify_wpm(wpm, kademe):
    norms = get_wpm_norms(kademe)
    if wpm < norms["cok_yavas"]:
        return "cok_yavas", "Çok Yavaş", "🔴", "Okuma hızı yaş grubunun altında."
    elif wpm < norms["yavas"]:
        return "yavas", "Yavaş", "🟠", "Okuma hızı ortalamanın altında."
    elif wpm < norms["hizli"]:
        return "ortalama", "Ortalama", "🟡", "Okuma hızı yaş grubuna uygun."
    elif wpm < norms["cok_hizli"]:
        return "hizli", "Hızlı", "🔵", "Okuma hızı ortalamanın üzerinde."
    else:
        return "cok_hizli", "Çok Hızlı", "🟢", "Mükemmel okuma hızı!"

def calculate_speed_reading(answers, passage_data, reading_time_seconds, kademe):
    word_count = count_words(passage_data["text"])
    reading_time_minutes = reading_time_seconds / 60.0
    wpm = round(word_count / max(reading_time_minutes, 0.01))
    speed_key, speed_label, speed_emoji, speed_comment = classify_wpm(wpm, kademe)
    norms = get_wpm_norms(kademe)

    questions = passage_data["questions"]
    correct = 0
    detail = []
    for q in questions:
        user_ans = answers.get(q["id"], "")
        is_correct = (user_ans == q["answer"])
        if is_correct: correct += 1
        detail.append({"id": q["id"], "text": q["text"], "user": user_ans, "correct_answer": q["answer"], "is_correct": is_correct})

    total = len(questions)
    comprehension_pct = round(correct / max(total, 1) * 100, 1)

    if comprehension_pct >= 80: comp_level, comp_emoji = "Çok İyi", "🟢"
    elif comprehension_pct >= 60: comp_level, comp_emoji = "İyi", "🔵"
    elif comprehension_pct >= 40: comp_level, comp_emoji = "Orta", "🟡"
    elif comprehension_pct >= 20: comp_level, comp_emoji = "Düşük", "🟠"
    else: comp_level, comp_emoji = "Çok Düşük", "🔴"

    max_expected = norms["cok_hizli"] * 1.3
    speed_normalized = min(wpm / max_expected * 100, 100)
    effective_score = round(speed_normalized * 0.4 + comprehension_pct * 0.6, 1)

    if effective_score >= 80: eff_level, eff_emoji = "Mükemmel", "🟢"
    elif effective_score >= 65: eff_level, eff_emoji = "İyi", "🔵"
    elif effective_score >= 50: eff_level, eff_emoji = "Orta", "🟡"
    elif effective_score >= 35: eff_level, eff_emoji = "Gelişime Açık", "🟠"
    else: eff_level, eff_emoji = "Destek Gerekli", "🔴"

    if wpm >= norms["hizli"] and comprehension_pct >= 70:
        profile = "⚡ Hızlı & Anlayan Okuyucu"
        profile_desc = "Hem hızlı okuyor hem de anlıyorsun!"
    elif wpm >= norms["hizli"] and comprehension_pct < 50:
        profile = "💨 Hızlı Ama Yüzeysel"
        profile_desc = "Hızlısın ama anlamanı geliştirmen gerek."
    elif wpm < norms["yavas"] and comprehension_pct >= 70:
        profile = "🔍 Yavaş Ama Derinlemesine"
        profile_desc = "Yavaş ama iyi anlıyorsun."
    elif wpm < norms["yavas"] and comprehension_pct < 50:
        profile = "📖 Destek İhtiyacı"
        profile_desc = "Düzenli okuma alışkanlığı edinmek öncelikli."
    else:
        profile = "📚 Dengeli Okuyucu"
        profile_desc = "Dengeli bir okuma profilen var."

    return {
        "passage_title": passage_data["title"], "word_count": word_count,
        "reading_time_seconds": round(reading_time_seconds, 1),
        "reading_time_minutes": round(reading_time_minutes, 2),
        "wpm": wpm, "speed_key": speed_key, "speed_label": speed_label,
        "speed_emoji": speed_emoji, "speed_comment": speed_comment,
        "norms": norms, "kademe": kademe,
        "kademe_label": KADEME_LABELS.get(kademe, ""),
        "correct": correct, "total": total, "comprehension_pct": comprehension_pct,
        "comp_level": comp_level, "comp_emoji": comp_emoji, "detail": detail,
        "effective_score": effective_score, "eff_level": eff_level, "eff_emoji": eff_emoji,
        "profile": profile, "profile_desc": profile_desc,
    }

def generate_speed_reading_report(scores):
    norms = scores["norms"]
    def bar(pct):
        filled = int(pct / 5)
        return "█" * filled + "░" * (20 - filled)

    report = f"""# 📖 Hızlı Okuma & Anlama Raporu

## 📋 Test Bilgileri
| Bilgi | Değer |
|-------|-------|
| Metin | {scores['passage_title']} |
| Kademe | {scores['kademe_label']} |
| Kelime Sayısı | {scores['word_count']} |
| Okuma Süresi | {scores['reading_time_seconds']} sn ({scores['reading_time_minutes']} dk) |

---

## ⏱️ Okuma Hızı: {scores['speed_emoji']} {scores['wpm']} Kelime/Dakika — {scores['speed_label']}

{scores['speed_comment']}

## 🧠 Anlama: {scores['comp_emoji']} %{scores['comprehension_pct']} — {scores['comp_level']}

{scores['correct']}/{scores['total']} doğru cevap

{bar(scores['comprehension_pct'])} %{scores['comprehension_pct']}

## 🎯 Etkili Okuma: {scores['eff_emoji']} %{scores['effective_score']} — {scores['eff_level']}

## 🧑‍🎓 Profil: {scores['profile']}

{scores['profile_desc']}

---

## 📊 Soru Detayları

| # | Sonuç | Soru |
|---|-------|------|
"""
    for i, d in enumerate(scores["detail"], 1):
        icon = "✅" if d["is_correct"] else "❌"
        report += f"| {i} | {icon} | {d['text'][:60]}... |\n"

    return report.strip()

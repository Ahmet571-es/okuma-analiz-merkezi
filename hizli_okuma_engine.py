"""
Hızlı Okuma Testi Motoru
— Zamanlı okuma + anlama soruları + skor hesaplama
"""

# ─── HIZLI OKUMA METİNLERİ VE SORULARI ───────────────────────────────────────

HIZLI_OKUMA_VERILERI = {
    1: {
        "baslik": "Bahçedeki Hayvanlar",
        "metin": (
            "Elif'in evinin bahçesinde hayvanlar vardı. Bir köpek, iki kedi ve üç tavuk yaşardı. "
            "Köpeğin adı Karabaş'tı. Kedilerin biri beyaz, diğeri siyahtı. Tavuklar her gün yumurta yapardı. "
            "Elif her sabah tavukların yumurtalarını toplardı. Annesi bu yumurtalarla kahvaltı hazırlardı. "
            "Karabaş bahçeyi beklerdi. Kediler güneşte uyurdu. Elif hayvanlarını çok severdi."
        ),
        "sorular": [
            {"soru": "Elif'in bahçesinde kaç tür hayvan vardı?", "secenekler": ["2", "3", "4", "5"], "dogru": "3"},
            {"soru": "Köpeğin adı neydi?", "secenekler": ["Pamuk", "Karabaş", "Boncuk", "Çomar"], "dogru": "Karabaş"},
            {"soru": "Bahçede kaç tavuk vardı?", "secenekler": ["1", "2", "3", "4"], "dogru": "3"},
            {"soru": "Kedilerin rengi neydi?", "secenekler": ["İkisi beyaz", "Beyaz ve siyah", "İkisi siyah", "Beyaz ve gri"], "dogru": "Beyaz ve siyah"},
            {"soru": "Elif her sabah ne toplardı?", "secenekler": ["Çiçek", "Meyve", "Yumurta", "Sebze"], "dogru": "Yumurta"},
            {"soru": "Annesi yumurtalarla ne hazırlardı?", "secenekler": ["Akşam yemeği", "Öğle yemeği", "Kahvaltı", "Pasta"], "dogru": "Kahvaltı"},
            {"soru": "Karabaş ne yapardı?", "secenekler": ["Uyurdu", "Bahçeyi beklerdi", "Oynardı", "Koşardı"], "dogru": "Bahçeyi beklerdi"},
            {"soru": "Kediler nerede uyurdu?", "secenekler": ["Evde", "Güneşte", "Ağaçta", "Bahçede"], "dogru": "Güneşte"},
            {"soru": "Bahçede kaç kedi vardı?", "secenekler": ["1", "2", "3", "4"], "dogru": "2"},
            {"soru": "Elif hayvanlarına ne hissediyordu?", "secenekler": ["Korkardı", "Sevmezdi", "Çok severdi", "İlgilenmezdi"], "dogru": "Çok severdi"},
        ],
    },
    2: {
        "baslik": "Yağmurlu Gün",
        "metin": (
            "Bugün hava çok bulutluydu. Mehmet okula giderken yağmur başladı. Şemsiyesini almayı unutmuştu. "
            "Koşarak okulun kapısına ulaştı ama ıslanmıştı. Öğretmeni onu görünce endişelendi. "
            "Mehmet'e kuru bir havlu verdi. Mehmet saçlarını kuruladı. Teneffüste arkadaşları bahçeye çıktı "
            "ama Mehmet sınıfta kaldı. Pencereden yağmuru seyretti. Yağmur damlalarının cama vuruşunu dinledi. "
            "Okul çıkışında güneş açmıştı. Gökyüzünde güzel bir gökkuşağı vardı. Mehmet gökkuşağını "
            "görünce çok sevindi. Eve gülerek döndü."
        ),
        "sorular": [
            {"soru": "Hava nasıldı?", "secenekler": ["Güneşli", "Bulutlu", "Karlı", "Rüzgârlı"], "dogru": "Bulutlu"},
            {"soru": "Mehmet neyi unutmuştu?", "secenekler": ["Çantasını", "Şemsiyesini", "Ödevini", "Montunu"], "dogru": "Şemsiyesini"},
            {"soru": "Öğretmeni ona ne verdi?", "secenekler": ["Mont", "Çay", "Havlu", "Ekmek"], "dogru": "Havlu"},
            {"soru": "Teneffüste Mehmet ne yaptı?", "secenekler": ["Bahçeye çıktı", "Sınıfta kaldı", "Uyudu", "Kitap okudu"], "dogru": "Sınıfta kaldı"},
            {"soru": "Mehmet pencereden ne seyretti?", "secenekler": ["Kuşları", "Arabalar", "Yağmuru", "Arkadaşlarını"], "dogru": "Yağmuru"},
            {"soru": "Okul çıkışında hava nasıldı?", "secenekler": ["Yağmurlu", "Güneş açmıştı", "Bulutlu", "Karlı"], "dogru": "Güneş açmıştı"},
            {"soru": "Gökyüzünde ne vardı?", "secenekler": ["Bulut", "Yıldız", "Gökkuşağı", "Uçak"], "dogru": "Gökkuşağı"},
            {"soru": "Mehmet nereye gidiyordu?", "secenekler": ["Parka", "Okula", "Markete", "Eve"], "dogru": "Okula"},
            {"soru": "Mehmet okula nasıl ulaştı?", "secenekler": ["Yürüyerek", "Koşarak", "Arabayla", "Otobüsle"], "dogru": "Koşarak"},
            {"soru": "Mehmet eve nasıl döndü?", "secenekler": ["Ağlayarak", "Koşarak", "Gülerek", "Üzülerek"], "dogru": "Gülerek"},
        ],
    },
    3: {
        "baslik": "Karıncanın Dersi",
        "metin": (
            "Küçük Ahmet yazın sıcak bir gününde parkta oturuyordu. Bir dondurma yiyordu ve etrafı seyrediyordu. "
            "Birden yerde uzun bir karınca sırasını fark etti. Karıncalar bir ekmek kırıntısını taşımaya çalışıyordu. "
            "Kırıntı karıncaların boyutuna göre çok büyüktü. Ama karıncalar pes etmiyordu. Bazıları kırıntıyı "
            "iterken, bazıları çekerdi. Birlikte çalışarak kırıntıyı yuvalarına doğru taşıdılar.\n\n"
            "Ahmet bu manzarayı uzun süre izledi. Karıncaların birlikte çalışmasına hayran kaldı. Eve döndüğünde "
            "annesine karıncaları anlattı. Annesi gülümsedi ve dedi ki: Karıncalar bize takım çalışmasının "
            "gücünü öğretiyor. Tek başına taşıyamadıkları şeyleri birlikte taşıyabiliyorlar. Ahmet o gün "
            "önemli bir ders öğrendi: Birlikte çalışmak, en zor işleri bile kolaylaştırır."
        ),
        "sorular": [
            {"soru": "Ahmet neredeydi?", "secenekler": ["Evde", "Okulda", "Parkta", "Bahçede"], "dogru": "Parkta"},
            {"soru": "Ahmet ne yiyordu?", "secenekler": ["Sandviç", "Dondurma", "Simit", "Çikolata"], "dogru": "Dondurma"},
            {"soru": "Karıncalar ne taşıyordu?", "secenekler": ["Yaprak", "Ekmek kırıntısı", "Şeker", "Böcek"], "dogru": "Ekmek kırıntısı"},
            {"soru": "Kırıntı karıncalara göre nasıldı?", "secenekler": ["Küçüktü", "Çok büyüktü", "Hafifti", "Tam uygundu"], "dogru": "Çok büyüktü"},
            {"soru": "Karıncalar ne yapıyordu?", "secenekler": ["Pes ettiler", "Birlikte çalışıyordu", "Kavga ediyordu", "Uyuyordu"], "dogru": "Birlikte çalışıyordu"},
            {"soru": "Ahmet kırıntıyı nereye taşıdıklarını gördü?", "secenekler": ["Ağaca", "Suya", "Yuvalarına", "Çöpe"], "dogru": "Yuvalarına"},
            {"soru": "Ahmet eve dönünce kime anlattı?", "secenekler": ["Babasına", "Annesine", "Kardeşine", "Arkadaşına"], "dogru": "Annesine"},
            {"soru": "Annesi ne dedi?", "secenekler": ["Önemsiz", "Takım çalışmasının gücü", "Karıncalar zararlı", "Parkta oturma"], "dogru": "Takım çalışmasının gücü"},
            {"soru": "Mevsim neydi?", "secenekler": ["Kış", "İlkbahar", "Yaz", "Sonbahar"], "dogru": "Yaz"},
            {"soru": "Ahmet o gün ne öğrendi?", "secenekler": ["Dondurma yemeyi", "Birlikte çalışmanın gücünü", "Karınca türlerini", "Park kurallarını"], "dogru": "Birlikte çalışmanın gücünü"},
        ],
    },
    4: {
        "baslik": "Deniz Feneri Bekçisi",
        "metin": (
            "Yıllar önce küçük bir kıyı kasabasında yaşlı bir deniz feneri bekçisi yaşardı. Adı Hasan Dede'ydi. "
            "Her akşam fener kulesine çıkar ve ışığı yakardı. Bu ışık, geceleyin denizde yol alan gemilere rehberlik "
            "ederdi. Fırtınalı gecelerde bile Hasan Dede görevini asla ihmal etmezdi.\n\n"
            "Bir kış gecesi korkunç bir fırtına koptu. Rüzgâr uğulduyordu, dalgalar kayalıklara çarpıyordu. "
            "Hasan Dede fenerin ışığının söndüğünü fark etti. Hemen kuleye koştu. Merdivenleri tırmanırken "
            "rüzgâr onu sallıyordu ama durmadı. Feneri tekrar yaktığında, uzakta bir geminin ışıklarını gördü. "
            "Gemi tehlikeli kayalıklara doğru ilerliyordu. Fenerin ışığı sayesinde kaptan rotasını değiştirdi "
            "ve gemi kurtuldu.\n\n"
            "Ertesi gün geminin kaptanı kasabaya gelip Hasan Dede'yi buldu. Elini sıktı ve teşekkür etti. "
            "Hasan Dede mütevazı bir şekilde gülümsedi. O gece yine fenerin yanına çıktı, çünkü denizde "
            "her zaman birileri ışığa ihtiyaç duyardı."
        ),
        "sorular": [
            {"soru": "Hasan Dede ne iş yapardı?", "secenekler": ["Balıkçı", "Fener bekçisi", "Kaptan", "Öğretmen"], "dogru": "Fener bekçisi"},
            {"soru": "Fenerin görevi neydi?", "secenekler": ["Kasabayı aydınlatmak", "Gemilere rehberlik etmek", "Balıkları çekmek", "Fırtınayı durdurmak"], "dogru": "Gemilere rehberlik etmek"},
            {"soru": "Fırtına ne zaman koptu?", "secenekler": ["Yaz gecesi", "Kış gecesi", "Sonbahar sabahı", "İlkbahar akşamı"], "dogru": "Kış gecesi"},
            {"soru": "Fenerin ışığına ne oldu?", "secenekler": ["Parladı", "Söndü", "Kırıldı", "Zayıfladı"], "dogru": "Söndü"},
            {"soru": "Hasan Dede merdivenleri tırmanırken ne oluyordu?", "secenekler": ["Yağmur yağıyordu", "Rüzgâr onu sallıyordu", "Kar yağıyordu", "Deprem oluyordu"], "dogru": "Rüzgâr onu sallıyordu"},
            {"soru": "Gemi nereye ilerliyordu?", "secenekler": ["Limana", "Açık denize", "Tehlikeli kayalıklara", "Başka bir kasabaya"], "dogru": "Tehlikeli kayalıklara"},
            {"soru": "Kaptan ne yaptı?", "secenekler": ["Durdu", "Rotasını değiştirdi", "Geri döndü", "Yardım istedi"], "dogru": "Rotasını değiştirdi"},
            {"soru": "Ertesi gün kaptan ne yaptı?", "secenekler": ["Gitti", "Teşekkür etti", "Şikâyet etti", "Hediye gönderdi"], "dogru": "Teşekkür etti"},
            {"soru": "Hasan Dede fırtınada ne gösterdi?", "secenekler": ["Korku", "Sorumluluk", "Kayıtsızlık", "Heyecan"], "dogru": "Sorumluluk"},
            {"soru": "Hikâyenin ana mesajı nedir?", "secenekler": ["Fırtına tehlikelidir", "Görev bilinci önemlidir", "Gemiler hızlı gider", "Kış soğuktur"], "dogru": "Görev bilinci önemlidir"},
        ],
    },
    5: {
        "baslik": "Uzay İstasyonunda Bir Gün",
        "metin": (
            "Astronot Zeynep, Uluslararası Uzay İstasyonu'nda uyandı. Yer çekimi olmadığı için uyku tulumunun "
            "içinde havada süzülüyordu. Saati kontrol etti: sabah altı. Dünya'nın bir tarafı güneş ışığıyla "
            "aydınlanıyordu, diğer tarafı karanlıktı. Uzay istasyonu doksan dakikada Dünya'nın etrafında bir tur "
            "atıyordu, bu yüzden bir günde on altı kez gün doğumu görebiliyordu.\n\n"
            "Kahvaltısını hazırladı. Uzayda yemek yemek ilginç bir deneyimdi. Su damlacıkları havada yüzüyordu "
            "ve yiyecekleri özel kaplardan sıkarak yiyordu. Kahvaltıdan sonra laboratuvara geçti. Bugünkü "
            "görevi bitkilerin uzayda nasıl büyüdüğünü incelemekti. Küçük bir serada domates fideleri "
            "yetiştiriyordu. Yer çekimi olmadan köklerin farklı yönlere uzandığını gözlemledi.\n\n"
            "Öğleden sonra Dünya ile bağlantı kurdu. Bir okuldaki öğrencilerin sorularını yanıtladı. Çocuklar "
            "uzayda nasıl yıkandığını, uyuduğunu ve eğlendiğini merak ediyordu. Zeynep onlara uzayın ne kadar "
            "büyüleyici olduğunu anlattı. Akşam pencereden Dünya'yı seyrederken, mavi gezegenin ne kadar "
            "güzel ve kırılgan olduğunu bir kez daha hissetti."
        ),
        "sorular": [
            {"soru": "Zeynep nerede uyandı?", "secenekler": ["Evde", "Uçakta", "Uzay istasyonunda", "Okulda"], "dogru": "Uzay istasyonunda"},
            {"soru": "Neden havada süzülüyordu?", "secenekler": ["Uçuyordu", "Yer çekimi yoktu", "Rüzgâr vardı", "Parakütü vardı"], "dogru": "Yer çekimi yoktu"},
            {"soru": "İstasyon Dünya etrafında ne kadar sürede dönüyor?", "secenekler": ["60 dakika", "90 dakika", "120 dakika", "24 saat"], "dogru": "90 dakika"},
            {"soru": "Bir günde kaç kez gün doğumu görebiliyordu?", "secenekler": ["1", "8", "16", "24"], "dogru": "16"},
            {"soru": "Uzayda su nasıldı?", "secenekler": ["Donuyordu", "Havada yüzüyordu", "Buharlaşıyordu", "Kayboluyordu"], "dogru": "Havada yüzüyordu"},
            {"soru": "Zeynep'in laboratuvar görevi neydi?", "secenekler": ["Tamir", "Bitki incelemek", "Yemek yapmak", "Spor yapmak"], "dogru": "Bitki incelemek"},
            {"soru": "Ne yetiştiriyordu?", "secenekler": ["Çilek", "Domates", "Patates", "Biber"], "dogru": "Domates"},
            {"soru": "Kökler uzayda nasıl uzanıyordu?", "secenekler": ["Aşağı doğru", "Yukarı doğru", "Farklı yönlere", "Hiç uzanmıyordu"], "dogru": "Farklı yönlere"},
            {"soru": "Öğleden sonra ne yaptı?", "secenekler": ["Uyudu", "Öğrencilerin sorularını yanıtladı", "Yürüyüş yaptı", "Film izledi"], "dogru": "Öğrencilerin sorularını yanıtladı"},
            {"soru": "Dünya'yı nasıl tanımladı?", "secenekler": ["Büyük ve sert", "Mavi, güzel ve kırılgan", "Küçük ve soğuk", "Karanlık ve ürkütücü"], "dogru": "Mavi, güzel ve kırılgan"},
        ],
    },
    6: {
        "baslik": "Eski Mısır'ın Gizemi",
        "metin": (
            "Mısır piramitleri, insanlık tarihinin en etkileyici yapılarından biridir. Yaklaşık dört bin beş yüz "
            "yıl önce inşa edilen Büyük Giza Piramidi, uzun süre dünyanın en yüksek yapısı olma unvanını korumuştur. "
            "Bu devasa yapı, yaklaşık iki milyon üç yüz bin taş bloktan oluşur ve her bir blok ortalama iki buçuk "
            "ton ağırlığındadır.\n\n"
            "Piramitlerin nasıl inşa edildiği hâlâ tartışmalıdır. Bazı araştırmacılar rampa sistemleri kullanıldığını "
            "düşünürken, diğerleri iç rampa teorisini savunur. Kesin olan şu ki, bu yapılar dönemin matematik, "
            "astronomi ve mühendislik bilgisinin ne kadar ileri olduğunu göstermektedir. Piramitlerin kenarları "
            "neredeyse mükemmel bir şekilde kuzeye hizalanmıştır.\n\n"
            "Piramitler sadece birer mezar değildi. Firavunların ahiret hayatı için hazırlanan bu yapılarda "
            "yiyecekler, mücevherler, mobilyalar ve hatta hizmetkâr heykelleri bulunurdu. Mısırlılar ölümden "
            "sonraki yaşama inandıkları için cesetleri mumyalıyorlardı. Mumyalama süreci yaklaşık yetmiş gün "
            "sürerdi ve özel rahipler tarafından gerçekleştirilirdi.\n\n"
            "Bugün piramitler UNESCO Dünya Mirası Listesinde yer alır ve her yıl milyonlarca turist tarafından "
            "ziyaret edilir. Antik Mısır medeniyeti, bize insanın inanç, bilim ve kararlılıkla neler "
            "başarabileceğini gösteren muhteşem bir mirastır."
        ),
        "sorular": [
            {"soru": "Büyük Giza Piramidi kaç yıl önce inşa edildi?", "secenekler": ["2500", "3500", "4500", "5500"], "dogru": "4500"},
            {"soru": "Piramit kaç taş bloktan oluşur?", "secenekler": ["1.3 milyon", "2.3 milyon", "3.3 milyon", "4.3 milyon"], "dogru": "2.3 milyon"},
            {"soru": "Her taş blok ortalama kaç ton?", "secenekler": ["1.5 ton", "2.5 ton", "3.5 ton", "5 ton"], "dogru": "2.5 ton"},
            {"soru": "Piramitlerin kenarları neye hizalıdır?", "secenekler": ["Güneye", "Kuzeye", "Doğuya", "Batıya"], "dogru": "Kuzeye"},
            {"soru": "Piramitler kimin için yapılmıştır?", "secenekler": ["Halk", "Askerler", "Firavunlar", "Rahipler"], "dogru": "Firavunlar"},
            {"soru": "Piramitlerin içinde ne bulunurdu?", "secenekler": ["Sadece mumya", "Yiyecek ve mücevher", "Hiçbir şey", "Silahlar"], "dogru": "Yiyecek ve mücevher"},
            {"soru": "Mumyalama süreci kaç gün sürerdi?", "secenekler": ["30 gün", "50 gün", "70 gün", "90 gün"], "dogru": "70 gün"},
            {"soru": "Mumyalama kim tarafından yapılırdı?", "secenekler": ["Askerler", "Özel rahipler", "Firavunlar", "Halk"], "dogru": "Özel rahipler"},
            {"soru": "Piramitler hangi listede yer alır?", "secenekler": ["Forbes", "UNESCO Dünya Mirası", "Guinness", "National Geographic"], "dogru": "UNESCO Dünya Mirası"},
            {"soru": "Metnin ana fikri nedir?", "secenekler": ["Piramitler güzeldir", "Mısır medeniyetinin ileri düzeyi", "Turizm önemlidir", "Mumyalama ilginçtir"], "dogru": "Mısır medeniyetinin ileri düzeyi"},
        ],
    },
    7: {
        "baslik": "Beyin ve Öğrenme",
        "metin": (
            "İnsan beyni, evrendeki en karmaşık yapılardan biridir. Yaklaşık yüz milyar sinir hücresinden oluşan "
            "beyin, bu hücrelerin arasındaki trilyonlarca bağlantıyla çalışır. Her yeni bilgi öğrendiğimizde, "
            "beynimizde yeni sinaptik bağlantılar oluşur. Bu süreç nöroplastisite olarak adlandırılır ve "
            "beynimizin yaşam boyu değişip gelişebileceği anlamına gelir.\n\n"
            "Araştırmalar, öğrenmenin en etkili yollarının pasif dinleme olmadığını gösteriyor. Aktif öğrenme, "
            "yani bilgiyi sorgulamak, tartışmak ve uygulamak, beynin daha güçlü bağlantılar kurmasını sağlar. "
            "Bir konuyu başkasına öğretmek, öğrenmenin en etkili yollarından biridir. Buna öğretme etkisi denir.\n\n"
            "Uyku, öğrenme için kritik öneme sahiptir. Gün içinde öğrendiğimiz bilgiler, uyku sırasında uzun "
            "süreli belleğe aktarılır. Yeterli uyumayan öğrencilerin öğrenme kapasitesi önemli ölçüde düşer. "
            "Egzersiz de beyin sağlığı için vazgeçilmezdir. Fiziksel aktivite beyne daha fazla kan ve oksijen "
            "taşır, bu da yeni sinir hücrelerinin oluşmasını destekler.\n\n"
            "Stres ise öğrenmenin düşmanıdır. Yüksek stres altında kortizol hormonu salgılanır ve bu hormon "
            "bellek oluşumunu engeller. Bu nedenle sınav kaygısı yaşayan öğrenciler, bildikleri şeyleri bile "
            "hatırlayamayabilir. Nefes egzersizleri, düzenli çalışma ve olumlu düşünme stresi azaltmaya yardımcı olur.\n\n"
            "Özetle, beynimiz inanılmaz bir öğrenme makinesidir. Onu doğru beslemek, yeterince uyumak, "
            "aktif öğrenme yöntemlerini kullanmak ve stresi yönetmek, akademik başarının anahtarlarıdır."
        ),
        "sorular": [
            {"soru": "İnsan beyninde kaç sinir hücresi vardır?", "secenekler": ["1 milyar", "10 milyar", "100 milyar", "1 trilyon"], "dogru": "100 milyar"},
            {"soru": "Yeni bağlantılar oluşması sürecine ne denir?", "secenekler": ["Nöroloji", "Nöroplastisite", "Nörotransmisyon", "Nörojenez"], "dogru": "Nöroplastisite"},
            {"soru": "En etkili öğrenme yolu hangisidir?", "secenekler": ["Pasif dinleme", "Aktif öğrenme", "Ezber", "Video izleme"], "dogru": "Aktif öğrenme"},
            {"soru": "Öğretme etkisi nedir?", "secenekler": ["Öğretmen olmak", "Başkasına öğreterek öğrenmek", "Kitap okumak", "Not tutmak"], "dogru": "Başkasına öğreterek öğrenmek"},
            {"soru": "Uyku sırasında bilgi nereye aktarılır?", "secenekler": ["Kısa süreli bellek", "Uzun süreli bellek", "Bilinçaltı", "Refleks bellek"], "dogru": "Uzun süreli bellek"},
            {"soru": "Egzersiz beyne ne sağlar?", "secenekler": ["Daha az enerji", "Daha fazla kan ve oksijen", "Daha az bağlantı", "Daha az uyku"], "dogru": "Daha fazla kan ve oksijen"},
            {"soru": "Stres altında hangi hormon salgılanır?", "secenekler": ["Dopamin", "Serotonin", "Kortizol", "Adrenalin"], "dogru": "Kortizol"},
            {"soru": "Kortizol ne yapar?", "secenekler": ["Belleği güçlendirir", "Bellek oluşumunu engeller", "Uyku düzenler", "Mutlu eder"], "dogru": "Bellek oluşumunu engeller"},
            {"soru": "Sınav kaygısı ne yapar?", "secenekler": ["Daha iyi hatırlatır", "Bilinenlerin hatırlanmasını zorlaştırır", "Konsantrasyonu artırır", "Hiçbir etkisi yok"], "dogru": "Bilinenlerin hatırlanmasını zorlaştırır"},
            {"soru": "Akademik başarının anahtarı hangisi DEĞİLDİR?", "secenekler": ["Yeterli uyku", "Aktif öğrenme", "Yüksek stres", "Egzersiz"], "dogru": "Yüksek stres"},
        ],
    },
    8: {
        "baslik": "İklim Değişikliği ve Geleceğimiz",
        "metin": (
            "Dünya'nın ortalama sıcaklığı sanayi devriminden bu yana yaklaşık bir virgül bir derece artmıştır. "
            "Bu rakam küçük görünse de etkileri devasa boyutlardadır. Kutup buzulları eriyor, deniz seviyeleri "
            "yükseliyor, aşırı hava olayları sıklaşıyor ve ekosistemler bozuluyor. Bilim insanları, bu "
            "değişikliklerin büyük ölçüde insan faaliyetlerinden kaynaklandığı konusunda hemfikir.\n\n"
            "Fosil yakıtların yakılması, ormansızlaşma ve endüstriyel süreçler atmosfere büyük miktarda sera "
            "gazı salıyor. Bu gazlar güneşten gelen ısıyı atmosferde hapsederek sera etkisi yaratıyor. "
            "Karbondioksit, metan ve diazot monoksit başlıca sera gazlarıdır. Özellikle karbondioksit "
            "seviyesi, son sekiz yüz bin yılın en yüksek düzeyine ulaşmıştır.\n\n"
            "İklim değişikliğinin etkileri eşit dağılmıyor. Küçük ada devletleri yükselen deniz seviyesi "
            "nedeniyle varlık tehlikesiyle karşı karşıya. Afrika ve Güney Asya'daki tarım toplulukları "
            "kuraklık ve sel felaketlerinden en çok etkilenen gruplar arasında. Paradoks olarak, iklim "
            "değişikliğine en az katkıda bulunan ülkeler en çok zarar görüyor.\n\n"
            "Çözümler hem bireysel hem de küresel düzeyde olmalı. Yenilenebilir enerji kaynaklarına geçiş, "
            "enerji verimliliğinin artırılması, sürdürülebilir tarım ve ormancılık uygulamaları ile karbon "
            "yakalama teknolojileri mücadelenin temel unsurları. Bireysel olarak ise enerji tasarrufu yapmak, "
            "toplu taşıma kullanmak, geri dönüşüme önem vermek ve bilinçli tüketim alışkanlıkları "
            "geliştirmek herkesin yapabileceği katkılardır.\n\n"
            "Paris İklim Anlaşması kapsamında ülkeler, küresel sıcaklık artışını iki derecenin altında "
            "tutmayı ve mümkünse bir virgül beş dereceyle sınırlamayı hedefliyor. Bu hedefe ulaşmak, "
            "insanlığın gelecek nesillere karşı en büyük sorumluluklarından biridir."
        ),
        "sorular": [
            {"soru": "Sanayi devriminden bu yana sıcaklık kaç derece arttı?", "secenekler": ["0.5°C", "1.1°C", "2.0°C", "3.5°C"], "dogru": "1.1°C"},
            {"soru": "Sera etkisi nasıl oluşur?", "secenekler": ["Güneş büyür", "Gazlar ısıyı atmosferde hapseder", "Okyanuslar ısınır", "Buzullar erir"], "dogru": "Gazlar ısıyı atmosferde hapseder"},
            {"soru": "Hangisi sera gazı DEĞİLDİR?", "secenekler": ["Karbondioksit", "Metan", "Oksijen", "Diazot monoksit"], "dogru": "Oksijen"},
            {"soru": "CO2 seviyesi kaç yılın en yükseğinde?", "secenekler": ["100.000", "500.000", "800.000", "1.000.000"], "dogru": "800.000"},
            {"soru": "Küçük ada devletlerinin sorunu nedir?", "secenekler": ["Deprem", "Yükselen deniz seviyesi", "Volkan", "Tsunami"], "dogru": "Yükselen deniz seviyesi"},
            {"soru": "İklim değişikliğine en az katkıda bulunan ülkeler ne yaşıyor?", "secenekler": ["En az zarar", "En çok fayda", "En çok zarar", "Hiçbir etki yok"], "dogru": "En çok zarar"},
            {"soru": "Hangisi çözüm önerisi DEĞİLDİR?", "secenekler": ["Yenilenebilir enerji", "Daha fazla fosil yakıt", "Geri dönüşüm", "Enerji tasarrufu"], "dogru": "Daha fazla fosil yakıt"},
            {"soru": "Paris Anlaşması hedefi nedir?", "secenekler": ["Sıcaklık artışını 2°C altında tutmak", "Tüm fabrikaları kapatmak", "Arabaları yasaklamak", "Ormanları korumak"], "dogru": "Sıcaklık artışını 2°C altında tutmak"},
            {"soru": "Bireysel olarak ne yapabiliriz?", "secenekler": ["Hiçbir şey", "Enerji tasarrufu ve geri dönüşüm", "Sadece hükümet çözebilir", "Daha fazla tüketim"], "dogru": "Enerji tasarrufu ve geri dönüşüm"},
            {"soru": "Metnin temel mesajı nedir?", "secenekler": ["İklim değişikliği doğal", "Bireysel ve küresel çözüm şart", "Teknoloji her şeyi çözer", "Sorun abartılıyor"], "dogru": "Bireysel ve küresel çözüm şart"},
        ],
    },
}


def get_speed_reading_data(grade: int) -> dict:
    """Sınıf düzeyine uygun hızlı okuma verisini döndürür."""
    return HIZLI_OKUMA_VERILERI.get(grade, HIZLI_OKUMA_VERILERI[4])


def calculate_speed_reading_score(wpm: float, correct_answers: int, total_questions: int = 10) -> dict:
    """Hızlı okuma skorunu hesaplar."""
    comprehension_pct = (correct_answers / total_questions) * 100
    effective_speed = wpm * (comprehension_pct / 100)
    
    # Seviye belirleme
    if effective_speed >= 200:
        level = "🌟 Mükemmel"
        level_color = "#10B981"
    elif effective_speed >= 150:
        level = "🎯 Çok İyi"
        level_color = "#3B82F6"
    elif effective_speed >= 100:
        level = "✅ İyi"
        level_color = "#6366F1"
    elif effective_speed >= 60:
        level = "📊 Orta"
        level_color = "#F59E0B"
    else:
        level = "📈 Geliştirilmeli"
        level_color = "#EF4444"
    
    return {
        "wpm": round(wpm, 1),
        "comprehension_pct": round(comprehension_pct, 1),
        "effective_speed": round(effective_speed, 1),
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "level": level,
        "level_color": level_color,
    }

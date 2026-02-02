# 🎓 Dynamic Exam Schedule Creation System
## Dinamik Sınav Takvimi Oluşturma Sistemi

> Üniversitelerde sınav planlama sürecini **otomatikleştiren**, **çakışmaları önleyen** ve **derslik kapasitesini optimize eden** Python tabanlı masaüstü uygulaması.

---

## 🚀 Proje Özeti

Bu proje, üniversitelerde sınav dönemlerinde ortaya çıkan **karmaşık, zaman alıcı ve hataya açık** sınav planlama sürecini otomatik hale getirmek amacıyla geliştirilmiştir.

Sistem; dersler, öğrenciler, öğretim üyeleri, derslik kapasiteleri ve tarihsel kısıtları aynı anda değerlendirerek **çakışmasız, dengeli ve uygulanabilir** bir sınav takvimi üretir.

Manuel yöntemlerin neden olduğu:
- öğrenci sınav çakışmaları  
- derslik kapasite aşımı  
- zaman kaybı  
- insan kaynaklı hatalar  

bu sistem sayesinde **minimum seviyeye indirilir**.

---

## 🧠 Temel Özellikler

### 🔹 Otomatik Sınav Planlama
- Öğrenci bazlı sınav çakışma analizi
- Aynı öğrencinin aynı anda birden fazla sınava girmesini engelleme
- Sınavlar arasında minimum bekleme süresi tanımlayabilme
- Tatil ve istenmeyen günlerin otomatik dışlanması

### 🔹 Derslik ve Kapasite Optimizasyonu
- Derslik kapasite uygunluk kontrolü
- En uygun dersliklerin otomatik atanması
- Derslik kullanımının maksimum verimle sağlanması

### 🔹 Rol Tabanlı Yetkilendirme
- **Admin**
  - Tüm bölümlere erişim
  - Kullanıcı yönetimi
  - Sistem genelinde tam yetki
- **Bölüm Koordinatörü**
  - Sadece kendi bölümüne ait ders, öğrenci ve sınav işlemleri
  - Oturma planı ve sınav programı oluşturma

### 🔹 Excel Entegrasyonu
- Ders listelerinin Excel üzerinden toplu yüklenmesi
- Öğrenci–ders eşleştirmelerinin otomatik işlenmesi
- Satır bazlı hata tespiti ve kullanıcıya geri bildirim

### 🔹 Oturma Planı ve PDF Çıktı
- Dersliklerin satır–sütun yapısına göre oturma düzeni oluşturma
- Öğrenci bazlı koltuk yerleşimi
- Gözetmenler ve idari birimler için PDF çıktısı

---

## 🏗️ Yazılım Mimarisi

```text
UI (PyQt5)
│
├── Service Layer
│   ├── İş mantığı
│   ├── Sınav planlama algoritmaları
│   └── Kapasite ve çakışma kontrolleri
│
├── Repository Layer
│   └── MySQL CRUD işlemleri
│
└── Database (MySQL)


Bu yapı sayesinde:
- UI, iş mantığı ve veri erişimi birbirinden ayrılmıştır
- Kod okunabilirliği ve sürdürülebilirliği artırılmıştır
- Sistem kolayca genişletilebilir hale getirilmiştir

---

## ⚙️ Kullanılan Teknolojiler

- **Python** – Ana programlama dili  
- **PyQt5** – Masaüstü kullanıcı arayüzü  
- **MySQL** – İlişkisel veritabanı  
- **bcrypt** – Güvenli parola hashleme  
- **ReportLab** – PDF oturma planı çıktıları  
- **Excel Parsing** – Toplu veri aktarımı  

---

## 🧩 Sınav Planlama Algoritması (Özet)

1. Ders, öğrenci ve derslik verileri toplanır  
2. Öğrenci bazlı çakışma matrisi oluşturulur  
3. Belirlenen tarih aralığı ve tatil günleri filtrelenir  
4. Derslik kapasite uygunluğu kontrol edilir  
5. Çakışmalar minimum olacak şekilde zaman dilimleri atanır  
6. Uygunsuz durumlarda detaylı hata ve uyarılar üretilir  

Amaç: **maksimum uygulanabilirlik, minimum çakışma**

---

## 📄 Üretilen Çıktılar

- Sınav takvimi (Tablo / Excel)
- Ders bazlı oturma planı
- PDF salon çıktıları
- Detaylı hata ve uyarı mesajları

---

## 🔒 Güvenlik

- Kullanıcı parolaları **bcrypt** ile hashlenir
- Rol bazlı erişim kontrolü uygulanır
- Yetkisiz veri erişimi engellenir

---

## 📈 Neden Bu Proje?

- Gerçek hayatta karşılaşılan bir problemi çözer
- Algoritmik düşünme ve optimizasyon içerir
- Katmanlı yazılım mimarisi uygular
- Veritabanı tasarımı ve UI entegrasyonu barındırır
- Akademik ve profesyonel projelere uygun yapıdadır

Bu proje yalnızca çalışan bir uygulama değil,  
aynı zamanda **iyi tasarlanmış bir mühendislik çözümüdür**.

---

## 👨‍💻 Geliştirici

**Saffet Hakan Koçak**  
Computer Engineering Student – Kocaeli University

---

## 🔮 Gelecek Çalışmalar

- Web tabanlı sürüm
- Gözetmen planlama modülü
- Çoklu kampüs desteği
- Daha gelişmiş optimizasyon algoritmaları


Sistem, **katmanlı ve modüler** bir mimari yapıda tasarlanmıştır:


# 🎯 EFYS Profesyonel Menü Yapısı

**Proje:** EFYS - Enerji Faturalandırma ve Yönetim Sistemi  
**Versiyon:** 1.0  
**Tarih:** 26 Ocak 2026  
**Tasarım:** Glassmorphism + Dark Mode + Cyber-Industrial

---

## 📋 İçindekiler

1. [Menü Mimarisi](#menü-mimarisi)
2. [Ana Menü Grupları](#ana-menü-grupları)
3. [MUST-HAVE Menüler](#must-have-menüler)
4. [DIFFERENTIATOR Menüler](#differentiator-menüler)
5. [Kullanıcı Rolleri ve Yetkiler](#kullanıcı-rolleri-ve-yetkiler)
6. [Tasarım Kuralları](#tasarım-kuralları)

---

## 🏗️ Menü Mimarisi

### Hiyerarşik Yapı

```
EFYS
├── 📊 Dashboard (Ana Sayfa)
├── 📡 Okuma İşlemleri
├── 📈 Veri İzleme & Analiz
├── 💰 Faturalama & Tahakkuk
├── 👥 Abone Yönetimi
├── 📊 Raporlama
├── 🚀 Akıllı Sistemler (DIFFERENTIATOR)
└── ⚙️ Sistem Ayarları
```

### Öncelik Seviyeleri

| Seviye             | Açıklama                                                | Renk Kodu  |
| ------------------ | ------------------------------------------------------- | ---------- |
| **MUST-HAVE**      | Sistemin temel işlevselliği için zorunlu                | 🔴 Kırmızı |
| **NICE-TO-HAVE**   | Kullanıcı deneyimini artıran ek özellikler              | 🟡 Sarı    |
| **DIFFERENTIATOR** | Rakiplerden farklılaşmayı sağlayan yenilikçi özellikler | 🟢 Yeşil   |

---

## 📊 1. Dashboard (Ana Sayfa)

**İkon:** 📊  
**Öncelik:** MUST-HAVE  
**Açıklama:** Tüm sistemin özet görünümü, kritik metriklerin anlık takibi

### Alt Menüler

| Alt Menü           | İkon | Açıklama                                                     | Öncelik      |
| ------------------ | ---- | ------------------------------------------------------------ | ------------ |
| **Genel Bakış**    | 🏠   | Tüm OSB'nin toplam tüketim, fatura ve alarm özeti            | MUST-HAVE    |
| **Canlı İzleme**   | 📡   | Anlık güç, akım, gerilim değerlerinin real-time takibi       | MUST-HAVE    |
| **Reaktif Radar**  | 🎯   | Endüktif/Kapasitif enerji durumu ve ceza riski göstergesi    | MUST-HAVE    |
| **Alarm Merkezi**  | 🔔   | Kritik uyarılar, ceza riskleri, sistem hataları              | MUST-HAVE    |
| **Hızlı İşlemler** | ⚡   | Sık kullanılan işlemlere kısayollar (Fatura Kes, Okuma Yap)  | NICE-TO-HAVE |

### Görsel Bileşenler

- **Reaktif Enerji Gauge Chart** (Doughnut - %0-20 arası)
- **Günlük Tüketim Line Chart** (Son 7 gün)
- **Fatura Dağılımı Pie Chart** (Abonelere göre)
- **Alarm Listesi** (Son 10 kritik olay)
- **KPI Kartları** (Toplam Tüketim, Aktif Abone, Ödeme Oranı)

---

- 

---

## 📡 3. Okuma İşlemleri

**İkon:** 📡  
**Öncelik:** MUST-HAVE  
**Açıklama:** Sayaçlardan veri okuma, zamanlanmış görevler ve manuel sorgular

### Alt Menüler

| Alt Menü                    | İkon | Açıklama                                           | Öncelik      |
| --------------------------- | ---- | -------------------------------------------------- | ------------ |
| **Anlık Okuma (On-Demand)** | ⚡   | "Oku" butonuna basarak anlık endeks çekme          | MUST-HAVE    |
| **Zamanlanmış Görevler**    | ⏰   | Otomatik okuma planları (Günlük, Saatlik, Aylık)   | MUST-HAVE    |
| **Toplu Okuma**             | 📊   | Seçili sayaç grubunu aynı anda okuma               | MUST-HAVE    |
| **Okuma Geçmişi**           | 📜   | Geçmiş okuma kayıtları ve başarı oranları          | MUST-HAVE    |
| **Başarısız Okumalar**      | ❌   | Okunamayan sayaçların listesi ve retry mekanizması | MUST-HAVE    |
| **Okuma Profilleri**        | 📋   | Farklı okuma senaryoları (Hızlı, Detaylı, Profil)  | NICE-TO-HAVE |

### Özellikler

- **Cron Job Scheduler:** Esnek zamanlama (Her gün 00:00, Her Pazartesi 08:00)
- **Retry Mekanizması:** Başarısız okumalarda otomatik tekrar deneme
- **Öncelik Sıralaması:** Kritik sayaçları önce okuma
- **Paralel Okuma:** Aynı anda birden fazla sayaç okuma (Thread pool)

---

## 📈 4. Veri İzleme & Analiz

**İkon:** 📈  
**Öncelik:** MUST-HAVE  
**Açıklama:** Sayaç verilerinin görselleştirilmesi, analiz ve doğrulama

### Alt Menüler

| Alt Menü                       | İkon | Açıklama                                         | Öncelik      |
| ------------------------------ | ---- | ------------------------------------------------ | ------------ |
| **Son Endeksler**              | 📊   | T1, T2, T3, Endüktif, Kapasitif son değerler     | MUST-HAVE    |
| **Yük Profili (Load Profile)** | 📉   | 15 dakikalık detaylı tüketim eğrileri            | MUST-HAVE    |
| **VEE (Veri Doğrulama)**       | ✅   | Veri doğrulama kuralları ve anomali tespiti      | MUST-HAVE    |
| **Eksik Veri Tamamlama**       | 🔄   | Okunamayan saatlerin tahmini doldurulması        | MUST-HAVE    |
| **Kayıp/Kaçak Analizi**        | 🔍   | Ana sayaç vs süzme sayaçlar fark analizi         | MUST-HAVE    |
| **Sanal Sayaç**                | 🎯   | Matematiksel gruplama (Tüm Tekstil Toplamı)      | NICE-TO-HAVE |

### VEE (Validation, Estimation, Editing) Kuralları

1. **Mantık Kontrolleri:**
   - Tüketim bir anda %500 artamaz
   - Negatif değer olamaz
   - Endeks geriye gidemez

2. **Tahmin Algoritmaları:**
   - Geçmiş ortalama (Son 30 gün)
   - Benzer gün analizi (Aynı haftanın günü)
   - Lineer interpolasyon

3. **Otomatik Düzeltme:**
   - Spike (Ani sıçrama) temizleme
   - Outlier (Aykırı değer) filtreleme

---

## 💰 5. Faturalama & Tahakkuk

**İkon:** 💰  
**Öncelik:** MUST-HAVE  
**Açıklama:** Fatura hesaplama, tahakkuk ve tahsilat yönetimi

### Alt Menüler

| Alt Menü                  | İkon | Açıklama                                             | Öncelik      |
| ------------------------- | ---- | ---------------------------------------------------- | ------------ |
| **Tarife Yönetimi**       | 📋   | T1, T2, T3 birim fiyatları ve zaman dilimleri        | MUST-HAVE    |
| **Dönem Açma/Kapama**     | 📅   | Fatura kesim döneminin başlatılması (Örn: 2025 Ocak) | MUST-HAVE    |
| **Fatura Hesapla**        | 🧮   | Endeks farkı × Birim fiyat hesaplaması               | MUST-HAVE    |
| **Toplu Fatura Kes**      | 📊   | Tüm abonelere aynı anda fatura kesme                 | MUST-HAVE    |
| **Fatura Önizleme**       | 👁️   | Fatura kesmeden önce detaylı önizleme                | MUST-HAVE    |
| **Ek Tahakkuk**           | ➕   | Manuel ceza, açma-kapama bedeli ekleme               | MUST-HAVE    |
| **Fatura İptali**         | ❌   | Hatalı faturanın iptali ve yeniden kesim             | MUST-HAVE    |
| **Fatura Yazdır/PDF**     | 🖨️   | Fatura çıktısı alma (PDF, Excel)                     | MUST-HAVE    |
| **E-Fatura Entegrasyonu** | 📧   | GİB e-Fatura sistemine otomatik gönderim             | NICE-TO-HAVE |
| **Toplu SMS/Email**       | 📱   | Fatura hazır bildirimi gönderme                      | NICE-TO-HAVE |

### Fatura Hesaplama Motoru

```
Toplam Tutar = (T1_Tüketim × T1_Fiyat) +
               (T2_Tüketim × T2_Fiyat) +
               (T3_Tüketim × T3_Fiyat) +
               (Reaktif_Tüketim × Reaktif_Fiyat) +
               Ek_Bedeller -
               İndirimler
```

### Reaktif Ceza Hesaplama

- **Endüktif:** Aktif enerjinin %20'sini aşarsa ceza
- **Kapasitif:** Aktif enerjinin %15'ini aşarsa ceza
- **Ceza Oranı:** Aşan kısım için %2 ek ücret

---

## 👥 6. Abone Yönetimi

**İkon:** 👥  
**Öncelik:** MUST-HAVE  
**Açıklama:** Abone bilgileri, sözleşmeler ve tahsilat takibi

### Alt Menüler

| Alt Menü              | İkon | Açıklama                                         | Öncelik   |
| --------------------- | ---- | ------------------------------------------------ | --------- |
| **Abone Kartı**       | 👤    | Firma ünvanı, vergi no, adres, yetkili bilgileri | MUST-HAVE |
| **Sözleşme Yönetimi** | 📄    | Sözleşme gücü, tarife grubu, başlangıç tarihi    | MUST-HAVE |

### Abone Tipleri

- **Sanayi:** Fabrika, üretim tesisi
- **Ticarethane:** Mağaza, ofis
- **Mesken:** Konut (OSB içi lojmanlar)
- **Kamu:** Belediye, okul

---

## 📊 7. Raporlama

**İkon:** 📊  
**Öncelik:** MUST-HAVE  
**Açıklama:** Detaylı raporlar, analizler ve Excel dökümler

### Alt Menüler

| Alt Menü                   | İkon | Açıklama                                     | Öncelik      |
| -------------------------- | ---- | -------------------------------------------- | ------------ |
| **Endeks Raporu**          | 📈   | Tarih aralığındaki ilk/son endeksler (Excel) | MUST-HAVE    |
| **Tüketim Raporu**         | ⚡   | Günlük, haftalık, aylık tüketim analizi      | MUST-HAVE    |
| **Fatura Raporu**          | 💰   | Dönemsel fatura özeti ve tahsilat durumu     | MUST-HAVE    |
| **Okuma Başarısı**         | 📊   | Toplam sayaçtan kaçı okundu? (SLA)           | MUST-HAVE    |
| **Kayıp/Kaçak Raporu**     | 🔍   | Ana sayaç vs süzme sayaçlar fark analizi     | MUST-HAVE    |
| **Reaktif Enerji Raporu**  | 🎯   | Endüktif/Kapasitif enerji ve ceza durumu     | MUST-HAVE    |
| **Demant Raporu**          | 📊   | Maksimum güç (Puant) analizi                 | MUST-HAVE    |
| **Abone Bazlı Rapor**      | 👥   | Abone özelinde detaylı tüketim/fatura        | MUST-HAVE    |
| **Karşılaştırmalı Rapor**  | 📉   | Dönemler arası karşılaştırma (YoY, MoM)      | NICE-TO-HAVE |
| **Grafik Raporlar**        | 📊   | Görsel grafiklerle sunumlar                  | NICE-TO-HAVE |
| **Özel Rapor Tasarlayıcı** | 🎨   | Kullanıcının kendi raporunu oluşturması      | NICE-TO-HAVE |

### Rapor Formatları

- **Excel (.xlsx):** Detaylı veri analizi için
- **PDF:** Resmi sunumlar ve arşivleme
- **CSV:** Dış sistemlere veri aktarımı
- **JSON/XML:** API entegrasyonları

### Otomatik Raporlama

- **Zamanlanmış Raporlar:** Her ayın 1'inde otomatik rapor oluştur
- **Email Gönderimi:** Raporu otomatik olarak yöneticilere gönder
- **Dashboard Widget:** Raporları dashboard'da görselleştir

---

## 🚀 8. Akıllı Sistemler (DIFFERENTIATOR)

**İkon:** 🚀  
**Öncelik:** DIFFERENTIATOR  
**Açıklama:** EFYS'yi rakiplerden ayıran yenilikçi özellikler

### Alt Menüler

| Alt Menü                   | İkon | Açıklama                                    | Rakiplerde Durum |
| -------------------------- | ---- | ------------------------------------------- | ---------------- |
| **🤖 Mevzuat TAKIP SISTEMI** | 📜   | Resmi Gazete otomatik takip ve bildirim     | ❌ YOK           |
| **⚖️ Ceza Önleme Sistemi** | 🛡️   | Proaktif uyarı (Reaktif sınıra yaklaştınız) | ❌ YOK           |
| **📱 Sanayici Portalı**    | 👤   | Mobil uygulama ile anlık tüketim görme      | 🟡 KISITLI       |
| **🔄 ERP Köprüsü**         | 🔗   | Logo/SAP/Netsis'e otomatik fiş atma         | 🟡 ZOR           |

### 🤖 Mevzuat takıp sıstemi Detayları

**İşlev:**

- Her sabah 08:00'da Resmi Gazete'yi otomatik tarar
- Enerji, elektrik, tarife ile ilgili değişiklikleri tespit eder
- Yöneticiye email/SMS ile bildirim gönderir
- Değişikliği sisteme otomatik uygular (Tarife güncellemesi)

**Örnek Senaryo:**

```
🔔 Mevzuat Değişikliği Tespit Edildi!

Tarih: 15 Ocak 2025
Kaynak: Resmi Gazete - Sayı 32450
Konu: Sanayi Tarifesi T1 Birim Fiyatı Güncellendi

Eski Fiyat: 3.452 TL/kWh
Yeni Fiyat: 3.678 TL/kWh
Yürürlük: 1 Şubat 2025

Aksiyon: Sisteme otomatik uygulandı ✅
```

### ⚖️ Ceza Önleme Sistemi 

**Proaktif Uyarılar:**

1. **Reaktif Enerji İzleme:**
   - Endüktif %15'e ulaştığında: "⚠️ Dikkat! %20 sınırına yaklaşıyorsunuz"
   - Endüktif %18'e ulaştığında: "🔴 Kritik! Kompanzasyon devreye alın"

2. **Demant Kontrolü:**
   - Sözleşme gücünün %90'ına ulaştığında uyarı
   - Aşma riski varsa otomatik yük kesme önerisi

3. **Ulusal Tarife Tavanı:**
   - Aylık tüketim tavanına yaklaşıldığında bildirim
   - Alternatif tüketim planı önerisi

### 📱 Sanayici Portalı (Mobil App)

**Özellikler:**

- Anlık tüketim görüntüleme (Real-time)
- Fatura geçmişi ve ödeme yapma
- Alarm bildirimleri (Push notification)
- QR kod ile sayaç okuma
- Destek talebi oluşturma

**Platform:** iOS + Android (React Native)

### 🤖 

### 🔄 ERP Köprüsü

**Desteklenen ERP'ler:**

- Logo Tiger
- SAP Business One
- Netsis
- Mikro
- Özel ERP'ler (API ile)

**Otomatik İşlemler:**

- Fatura kesildiğinde ERP'ye otomatik fiş atma
- Tahsilat girişinde ERP'yi güncelleme
- Cari hesap senkronizasyonu

---

## ⚙️ 9. Sistem Ayarları

**İkon:** ⚙️  
**Öncelik:** MUST-HAVE  
**Açıklama:** Sistem konfigürasyonu, kullanıcı yönetimi ve güvenlik

### Alt Menüler

| Alt Menü                 | İkon | Açıklama                                      | Öncelik      |
| ------------------------ | ---- | --------------------------------------------- | ------------ |
| **Kullanıcı Yönetimi**   | 👥   | Kullanıcı ekleme, rol atama, yetkilendirme    | MUST-HAVE    |
| **Rol ve Yetkiler**      | 🔐   | RBAC (Role-Based Access Control) tanımları    | MUST-HAVE    |
| **Sistem Parametreleri** | ⚙️   | Genel ayarlar (Dil, Saat Dilimi, Para Birimi) | MUST-HAVE    |
| **Email/SMS Ayarları**   | 📧   | SMTP, SMS gateway konfigürasyonu              | MUST-HAVE    |
| **Yedekleme**            | 💾   | Otomatik veritabanı yedekleme ayarları        | MUST-HAVE    |
| **Log Yönetimi**         | 📝   | Sistem logları, kullanıcı aktiviteleri        | MUST-HAVE    |
| **API Yönetimi**         | 🔌   | API key oluşturma, rate limiting              | NICE-TO-HAVE |
| **Entegrasyon Ayarları** | 🔗   | ERP, e-Fatura, Ödeme sistemleri               | NICE-TO-HAVE |
| **Güvenlik Ayarları**    | 🛡️   | 2FA, IP whitelist, şifre politikası           | MUST-HAVE    |
| **Lisans Yönetimi**      | 📜   | Lisans durumu, modül aktivasyonu              | MUST-HAVE    |

---

## 👤 Kullanıcı Rolleri ve Yetkiler

### Rol Tanımları

| Rol                  | Açıklama                   | Erişim Seviyesi |
| -------------------- | -------------------------- | --------------- |
| **Süper Admin**      | Tüm sistem yetkisi         | %100            |
| **OSB Yöneticisi**   | OSB genelinde tüm işlemler | %90             |
| **Fatura Sorumlusu** | Sadece faturalama modülü   | %40             |
| **Saha Teknisyeni**  | Cihaz yönetimi ve okuma    | %30             |
| **Muhasebe**         | Tahsilat ve raporlama      | %35             |
| **Sanayici (Abone)** | Sadece kendi verileri      | %10             |

### Yetki Matrisi

| Modül            | Süper Admin | OSB Yön. | Fatura Sor. | Saha Tek. | Muhasebe | Sanayici   |
| ---------------- | ----------- | -------- | ----------- | --------- | -------- | ---------- |
| Dashboard        | ✅          | ✅       | ✅          | ✅        | ✅       | ✅         |
| Cihaz Yönetimi   | ✅          | ✅       | ❌          | ✅        | ❌       | ❌         |
| Okuma İşlemleri  | ✅          | ✅       | ❌          | ✅        | ❌       | ❌         |
| Veri İzleme      | ✅          | ✅       | ✅          | ✅        | ✅       | 🟡 (Kendi) |
| Faturalama       | ✅          | ✅       | ✅          | ❌        | ✅       | 🟡 (Kendi) |
| Abone Yönetimi   | ✅          | ✅       | ✅          | ❌        | ✅       | ❌         |
| Raporlama        | ✅          | ✅       | ✅          | ✅        | ✅       | 🟡 (Kendi) |
| Akıllı Sistemler | ✅          | ✅       | 🟡          | ❌        | ❌       | ❌         |
| Sistem Ayarları  | ✅          | 🟡       | ❌          | ❌        | ❌       | ❌         |

**Açıklama:**

- ✅ Tam Erişim
- 🟡 Kısıtlı Erişim
- ❌ Erişim Yok

---

## 🎨 Tasarım Kuralları

### Menü Görünümü

**Sidebar Navigation (Sol Menü):**

```
┌─────────────────────────┐
│  🏢 EFYS               │
│  Enerji Yönetim Sistemi│
├─────────────────────────┤
│ 📊 Dashboard           │
│ ⚡ Cihaz Yönetimi      │
│ 📡 Okuma İşlemleri     │
│ 📈 Veri İzleme         │
│ 💰 Faturalama          │
│ 👥 Abone Yönetimi      │
│ 📊 Raporlama           │
│ 🚀 Akıllı Sistemler    │
│ ⚙️ Sistem Ayarları     │
└─────────────────────────┘
```

### Renk Kodları (OSOS Design System)

| Element                  | Renk      | Hex Code  |
| ------------------------ | --------- | --------- |
| **Primary (Ana Menü)**   | Purple    | `#8B5CF6` |
| **Secondary (Alt Menü)** | Blue      | `#3B82F6` |
| **Success (Başarılı)**   | Green     | `#10B981` |
| **Warning (Uyarı)**      | Amber     | `#F59E0B` |
| **Danger (Kritik)**      | Red       | `#EF4444` |
| **Background**           | Slate 900 | `#0F172A` |
| **Card Background**      | Slate 800 | `#1E293B` |
| **Text Primary**         | Slate 100 | `#F1F5F9` |

### Glassmorphism Efekti

```css
.menu-item {
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.menu-item:hover {
  background: rgba(139, 92, 246, 0.1);
  border-color: rgba(139, 92, 246, 0.3);
  transform: translateX(4px);
}

.menu-item.active {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}
```

### İkon Kullanımı

**Emoji İkonlar (Hızlı & Evrensel):**

- ✅ Tüm platformlarda çalışır
- ❌ Ek kütüphane gerektirmez
- 🎨 Renkli ve görsel

**Alternatif: Lucide Icons**

```html
<svg class="w-5 h-5" fill="none" stroke="currentColor">
  <path
    d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
  />
</svg>
```

### Responsive Tasarım

**Breakpoints:**

- **Mobile:** < 768px (Hamburger menü)
- **Tablet:** 768px - 1024px (Daraltılmış sidebar)
- **Desktop:** > 1024px (Tam sidebar)

**Mobile Menü:**

```
┌─────────────────┐
│ ☰  EFYS    👤  │
├─────────────────┤
│                 │
│  [Content]      │
│                 │
└─────────────────┘

[Hamburger tıklandığında]
┌─────────────────┐
│ ✕  Menü         │
├─────────────────┤
│ 📊 Dashboard    │
│ ⚡ Cihazlar     │
│ 📡 Okuma        │
│ ...             │
└─────────────────┘
```

---

## 📊 Menü İstatistikleri

### Toplam Menü Sayısı

| Kategori           | Ana Menü | Alt Menü | Toplam |
| ------------------ | -------- | -------- | ------ |
| **MUST-HAVE**      | 7        | 52       | 59     |
| **NICE-TO-HAVE**   | 0        | 15       | 15     |
| **DIFFERENTIATOR** | 1        | 8        | 9      |
| **TOPLAM**         | **8**    | **75**   | **83** |

### Modül Dağılımı

```
Dashboard (6 alt menü)           ████████░░ 7%

Okuma İşlemleri (7 alt menü)     █████████░ 8%
Veri İzleme (10 alt menü)        ███████████ 12%
Faturalama (10 alt menü)         ███████████ 12%
Abone Yönetimi (8 alt menü)      ██████████░ 10%
Raporlama (11 alt menü)          ████████████ 13%
Akıllı Sistemler (8 alt menü)    ██████████░ 10%
Sistem Ayarları (10 alt menü)    ███████████ 12%
```

---

## ✅ Implementation Checklist

### Faz 1: Temel Altyapı (Hafta 1-2)

- [ ] Menü veritabanı şeması oluştur
- [ ] RBAC (Role-Based Access Control) sistemi kur
- [ ] Sidebar navigation component'i geliştir
- [ ] Breadcrumb navigation ekle
- [ ] Mobile responsive menü

### Faz 2: MUST-HAVE Modüller (Hafta 3-8)

- [ ] Dashboard (Hafta 3)
- [ ] Cihaz Yönetimi (Hafta 4)
- [ ] Okuma İşlemleri (Hafta 5)
- [ ] Veri İzleme (Hafta 6)
- [ ] Faturalama (Hafta 7)
- [ ] Abone Yönetimi (Hafta 8)

### Faz 3: Raporlama & Analiz (Hafta 9-10)

- [ ] Raporlama modülü
- [ ] Excel/PDF export
- [ ] Grafik raporlar

### Faz 4: DIFFERENTIATOR Özellikler (Hafta 11-14)

- [ ] Mevzuat Botu (Hafta 11)
- [ ] Ceza Önleme Sistemi (Hafta 12)
- [ ] Sanayici Portalı (Hafta 13)
- [ ] Yapay Zeka Anomali (Hafta 14)

### Faz 5: Sistem Ayarları & Test (Hafta 15-16)

- [ ] Sistem ayarları modülü
- [ ] Entegrasyon testleri
- [ ] Kullanıcı kabul testleri (UAT)
- [ ] Performans optimizasyonu

---

## 🚀 Sonraki Adımlar

1. **Backend API Geliştirme:**
   - `menu_config.json` dosyasını kullanarak REST API endpoint'leri oluştur
   - `/api/menu/list` - Kullanıcı rolüne göre menü listesi
   - `/api/menu/permissions` - Yetki kontrolü

2. **Frontend Component Geliştirme:**
   - `menuler.html` mockup'ını React/Vue component'ine dönüştür
   - Sidebar navigation component
   - Breadcrumb component
   - Mobile hamburger menu

3. **Database Schema:**

   ```sql
   CREATE TABLE menu_items (
     id SERIAL PRIMARY KEY,
     parent_id INTEGER REFERENCES menu_items(id),
     name VARCHAR(100) NOT NULL,
     icon VARCHAR(50),
     route VARCHAR(200),
     priority VARCHAR(20), -- MUST-HAVE, NICE-TO-HAVE, DIFFERENTIATOR
     order_index INTEGER,
     is_active BOOLEAN DEFAULT true
   );

   CREATE TABLE menu_permissions (
     id SERIAL PRIMARY KEY,
     menu_id INTEGER REFERENCES menu_items(id),
     role_id INTEGER REFERENCES roles(id),
     can_view BOOLEAN DEFAULT false,
     can_edit BOOLEAN DEFAULT false,
     can_delete BOOLEAN DEFAULT false
   );
   ```

4. **Testing:**
   - Unit tests (Her menü item'ı için)
   - Integration tests (Yetki kontrolü)
   - E2E tests (Kullanıcı akışları)

---

**Versiyon:** 1.0  
**Son Güncelleme:** 26 Ocak 2026  
**Durum:** ✅ Dokümantasyon Tamamlandı

**Hazırlayan:** EFYS Development Team  
**Onaylayan:** OSB Yönetimi

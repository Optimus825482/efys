# EFYS Full Upgrade Plan

## Enerji Faturalandırma Yönetim Sistemi - Enterprise Upgrade

**Proje:** EFYS - Gönen OSB Enerji Yönetim Sistemi  
**Tarih:** 29 Ocak 2026  
**Versiyon:** 2.0 (Enterprise Upgrade)

---

## 🎯 Proje Özeti

Mevcut EFYS uygulamasının tüm modüllerini enterprise seviyesine çıkarma:

- **ECharts** ile interaktif grafikler
- **AG-Grid** ile gelişmiş tablolar
- **Trust Blue** tema optimizasyonu
- **PostgreSQL** entegrasyonu (tamamlandı)

---

## ✅ Tamamlanan İşler

| İş                                 | Durum | Tarih      |
| ---------------------------------- | ----- | ---------- |
| PostgreSQL şema oluşturma          | ✅    | 29.01.2026 |
| 30 Gönen OSB abonesi seed          | ✅    | 29.01.2026 |
| 83,520 okuma kaydı (demo)          | ✅    | 29.01.2026 |
| Dashboard gerçek veri entegrasyonu | ✅    | 29.01.2026 |
| Google Charts Gauge                | ✅    | 29.01.2026 |
| Ödeme modülü kaldırma              | ✅    | 29.01.2026 |

---

## 📋 Modül Güncelleme Planı

### PHASE 1: Core Infrastructure (Base)

#### 1.1 ECharts & AG-Grid Entegrasyonu

```
Dosya: templates/base.html
İşlem:
  - ECharts CDN ekleme
  - AG-Grid Enterprise CDN ekleme
  - Türkçe locale dosyaları
Süre: 15 dk
```

#### 1.2 CSS Design System Güncelleme

```
Dosya: static/css/style.css
İşlem:
  - MASTER.md'den renk değişkenleri
  - Plus Jakarta Sans font
  - AG-Grid tema özelleştirmesi
Süre: 20 dk
```

---

### PHASE 2: Okuma İşlemleri Modülü

#### 2.1 Anlık Okuma Sayfası

```
Dosya: templates/readings/instant.html
Route: routes/readings.py
İşlem:
  - Sayaç seçimi dropdown (gerçek veri)
  - Son okuma değerleri (ECharts gauge)
  - Okuma başlat butonu
  - Sonuç kartları
Süre: 30 dk
```

#### 2.2 Periyodik Okuma

```
Dosya: templates/readings/periodic.html
İşlem:
  - Zamanlama ayarları formu
  - Aktif görevler listesi (AG-Grid)
  - Okuma istatistikleri
Süre: 25 dk
```

#### 2.3 Okuma Geçmişi

```
Dosya: templates/readings/history.html
İşlem:
  - Tarih aralığı seçici
  - Abone/Sayaç filtresi
  - AG-Grid ile sayfalı tablo
  - Export (Excel, CSV)
Süre: 35 dk
```

---

### PHASE 3: Veri İzleme Modülü

#### 3.1 Canlı İzleme

```
Dosya: templates/monitoring/live.html
İşlem:
  - ECharts real-time line chart
  - WebSocket simülasyonu (setInterval)
  - Sayaç durumu kartları
  - Alarm bildirimleri
Süre: 45 dk
```

#### 3.2 Tüketim Analizi

```
Dosya: templates/monitoring/consumption.html
İşlem:
  - Dönemsel karşılaştırma (ECharts bar)
  - T1/T2/T3 dağılımı (ECharts pie)
  - Sektörel analiz
  - Trend çizgisi
Süre: 40 dk
```

#### 3.3 Reaktif Radar

```
Dosya: templates/monitoring/reactive.html
İşlem:
  - ECharts radar chart (tüm aboneler)
  - Güç faktörü tablosu (AG-Grid)
  - Ceza riski hesaplama
  - Detay modalları
Süre: 35 dk
```

#### 3.4 Kayıp/Kaçak Analizi

```
Dosya: templates/monitoring/loss.html
İşlem:
  - Trafo bazlı analiz
  - Kayıp oranı göstergeleri
  - Şüpheli tüketim tespiti
  - Harita görünümü (opsiyonel)
Süre: 40 dk
```

---

### PHASE 4: Faturalandırma Modülü

#### 4.1 Tarife Yönetimi

```
Dosya: templates/billing/tariffs.html
İşlem:
  - Tarife listesi (AG-Grid)
  - Yeni tarife modal
  - EPDK limit uyarıları
  - Tarife geçmişi
Süre: 30 dk
```

#### 4.2 Dönem Yönetimi

```
Dosya: templates/billing/period.html
İşlem:
  - Aktif dönem kartı
  - Dönem açma/kapatma
  - Dönem istatistikleri
Süre: 25 dk
```

#### 4.3 Fatura Hesaplama

```
Dosya: templates/billing/calculate.html
İşlem:
  - Abone seçimi (çoklu)
  - Hesaplama sonuçları (AG-Grid)
  - Toplu fatura oluşturma
  - Önizleme modalı
Süre: 40 dk
```

#### 4.4 Fatura Yazdırma

```
Dosya: templates/billing/print.html
İşlem:
  - Fatura şablonu
  - PDF export
  - Toplu yazdırma
Süre: 30 dk
```

---

### PHASE 5: Abone Yönetimi Modülü

#### 5.1 Abone Listesi

```
Dosya: templates/subscribers/index.html
İşlem:
  - AG-Grid ile tam özellikli tablo
  - Sektör/Durum filtresi
  - Toplu işlemler
  - Quick actions
Süre: 35 dk
```

#### 5.2 Abone Kartı (Ekleme/Düzenleme)

```
Dosya: templates/subscribers/card.html
İşlem:
  - Form validasyonu
  - Sayaç atama
  - Tarife seçimi
  - Adres bilgileri
Süre: 30 dk
```

#### 5.3 Abone Detay

```
Dosya: templates/subscribers/detail.html
İşlem:
  - Abone özet kartı
  - Tüketim trendi (ECharts)
  - Son okumalar tablosu
  - Fatura geçmişi
Süre: 40 dk
```

---

### PHASE 6: Raporlama Modülü

#### 6.1 Tüketim Raporu

```
Dosya: templates/reports/consumption.html
İşlem:
  - Tarih aralığı seçici
  - Sektörel dağılım
  - Grafikler + tablo
  - PDF/Excel export
Süre: 35 dk
```

#### 6.2 Mukayese Raporu

```
Dosya: templates/reports/comparison.html
İşlem:
  - Dönem karşılaştırma
  - Abone karşılaştırma
  - Yüzde değişim göstergeleri
Süre: 30 dk
```

#### 6.3 Maliyet Raporu

```
Dosya: templates/reports/cost.html
İşlem:
  - Maliyet analizi
  - Karlılık hesaplama
  - Projeksiyon grafikleri
Süre: 30 dk
```

---

### PHASE 7: Akıllı Sistemler Modülü

#### 7.1 Talep Tahmini

```
Dosya: templates/smart/prediction.html
İşlem:
  - ML-based tahmin simülasyonu
  - 7 günlük forecast (ECharts)
  - Güven aralıkları
Süre: 35 dk
```

#### 7.2 Anomali Tespiti

```
Dosya: templates/smart/anomaly.html
İşlem:
  - Anomali listesi
  - Şiddet sınıflandırma
  - Detay modalları
Süre: 30 dk
```

#### 7.3 Alarm Yönetimi

```
Dosya: templates/smart/alerts.html
İşlem:
  - Alarm kuralları (AG-Grid)
  - Kural ekleme modalı
  - Alarm geçmişi
Süre: 30 dk
```

---

### PHASE 8: Sistem Ayarları

#### 8.1 Genel Ayarlar

```
Dosya: templates/settings/general.html
İşlem: Form güncelleme
Süre: 15 dk
```

#### 8.2 Kullanıcı Yönetimi

```
Dosya: templates/settings/users.html
İşlem: AG-Grid tablo
Süre: 20 dk
```

#### 8.3 Veritabanı Ayarları

```
Dosya: templates/settings/database.html
İşlem: Bağlantı test butonu
Süre: 15 dk
```

#### 8.4 Yedekleme

```
Dosya: templates/settings/backup.html
İşlem: Yedek listesi, indirme
Süre: 15 dk
```

#### 8.5 Sistem Logları

```
Dosya: templates/settings/logs.html
İşlem: Filtrelenebilir log tablosu
Süre: 20 dk
```

---

## 🔧 Teknoloji Stack

### Frontend

| Kütüphane          | Versiyon | Kullanım          |
| ------------------ | -------- | ----------------- |
| ECharts            | 5.5.0    | Tüm grafikler     |
| AG-Grid Enterprise | 31.0     | Tüm tablolar      |
| Google Charts      | Latest   | Gauge (Dashboard) |
| Tailwind CSS       | 3.x      | Utility classes   |
| Plus Jakarta Sans  | -        | Typography        |

### Backend

| Kütüphane | Versiyon | Kullanım          |
| --------- | -------- | ----------------- |
| Flask     | 2.x      | Web framework     |
| psycopg2  | 2.x      | PostgreSQL driver |
| Jinja2    | 3.x      | Templates         |

### Database

| Sistem        | Kullanım       |
| ------------- | -------------- |
| PostgreSQL 15 | Ana veritabanı |
| 10 tablo      | Şema           |
| 83,520 kayıt  | Demo veri      |

---

## 📊 Tahmini Zaman

| Phase      | Modül            | Sayfa  | Süre         |
| ---------- | ---------------- | ------ | ------------ |
| 1          | Infrastructure   | 2      | 35 dk        |
| 2          | Okuma İşlemleri  | 3      | 90 dk        |
| 3          | Veri İzleme      | 4      | 160 dk       |
| 4          | Faturalandırma   | 4      | 125 dk       |
| 5          | Abone Yönetimi   | 3      | 105 dk       |
| 6          | Raporlama        | 3      | 95 dk        |
| 7          | Akıllı Sistemler | 3      | 95 dk        |
| 8          | Sistem Ayarları  | 5      | 85 dk        |
| **TOPLAM** | **8**            | **27** | **~13 saat** |

---

## ⚡ Uygulama Sırası

```
1. [PHASE 1] Base Infrastructure (ECharts + AG-Grid CDN)
2. [PHASE 2] Okuma İşlemleri (temel CRUD)
3. [PHASE 3] Veri İzleme (en kritik modül)
4. [PHASE 4] Faturalandırma (iş mantığı)
5. [PHASE 5] Abone Yönetimi (CRUD + detay)
6. [PHASE 6] Raporlama (analitik)
7. [PHASE 7] Akıllı Sistemler (ML simülasyonu)
8. [PHASE 8] Sistem Ayarları (polish)
```

---

## ✅ Onay Bekleniyor

Bu plan onaylanırsa implementasyona başlanacak.

**Sorular:**

1. Phase sırası uygun mu?
2. Herhangi bir modülü öne almak ister misin?
3. Ek özellik isteği var mı?

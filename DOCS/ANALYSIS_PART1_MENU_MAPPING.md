# EFYS - Kapsamlı Sistem Analizi - Bölüm 1: Menü-Sayfa-Veritabanı Mapping

**Tarih:** 29 Ocak 2026  
**Proje:** EFYS - Enerji Faturalandırma ve Yönetim Sistemi  
**Analiz Kapsamı:** Menü yapısı, route'lar, database fonksiyonları ve eksiklikler

---

## 📋 1. MENÜ-SAYFA-VERİTABANI MAPPING TABLOSU

### 1.1 Dashboard Modülü

| Menü Öğesi         | Route       | Template                         | Database Fonksiyonları                                                                                   | Durum             |
| ------------------ | ----------- | -------------------------------- | -------------------------------------------------------------------------------------------------------- | ----------------- |
| **Genel Bakış**    | `/`         | `dashboard/index.html`           | `get_dashboard_stats()`, `get_daily_consumption_chart()`, `get_reactive_status()`, `get_top_consumers()` | ✅ TAMAM          |
| **Canlı İzleme**   | `/live`     | `dashboard/live-monitoring.html` | ❌ EKSİK                                                                                                 | 🔴 EKSİK          |
| **Reaktif Radar**  | `/reactive` | `dashboard/reactive-radar.html`  | `get_reactive_status()`                                                                                  | ⚠️ TEMPLATE EKSİK |
| **Alarm Merkezi**  | `/alarms`   | `dashboard/alarm-center.html`    | ❌ EKSİK                                                                                                 | 🔴 EKSİK          |
| **Hızlı İşlemler** | -           | (Dashboard içinde)               | -                                                                                                        | ✅ TAMAM          |

**Eksik Fonksiyonlar:**

- `get_live_monitoring_data()` - Canlı izleme için real-time veri
- `get_alarms()` - Alarm listesi ve kritik uyarılar
- `get_alarm_stats()` - Alarm istatistikleri

---

### 1.2 Okuma İşlemleri Modülü

| Menü Öğesi               | Route                 | Template                  | Database Fonksiyonları                                   | Durum    |
| ------------------------ | --------------------- | ------------------------- | -------------------------------------------------------- | -------- |
| **Anlık Okuma**          | `/readings/instant`   | `readings/instant.html`   | `get_instant_readings()`, `get_reading_stats()`          | ✅ TAMAM |
| **Zamanlanmış Görevler** | `/readings/scheduled` | `readings/scheduled.html` | ❌ EKSİK                                                 | 🔴 EKSİK |
| **Toplu Okuma**          | `/readings/bulk`      | `readings/bulk.html`      | ❌ EKSİK                                                 | 🔴 EKSİK |
| **Okuma Geçmişi**        | `/readings/history`   | `readings/history.html`   | `get_readings_with_stats()`, `get_daily_reading_trend()` | ✅ TAMAM |
| **Başarısız Okumalar**   | `/readings/failed`    | `readings/failed.html`    | ❌ EKSİK                                                 | 🔴 EKSİK |

**Eksik Fonksiyonlar:**

- `get_scheduled_jobs()` - Zamanlanmış okuma görevleri
- `create_scheduled_job()` - Yeni görev oluşturma
- `get_bulk_reading_status()` - Toplu okuma durumu
- `start_bulk_reading()` - Toplu okuma başlatma
- `get_failed_readings()` - Başarısız okumalar listesi
- `retry_failed_reading()` - Başarısız okumayı tekrar deneme

---

### 1.3 Veri İzleme & Analiz Modülü

| Menü Öğesi               | Route                       | Template                        | Database Fonksiyonları                     | Durum    |
| ------------------------ | --------------------------- | ------------------------------- | ------------------------------------------ | -------- |
| **Son Endeksler**        | `/monitoring/last-indexes`  | `monitoring/last_indexes.html`  | `get_meter_indexes()`, `get_meter_stats()` | ✅ TAMAM |
| **Yük Profili**          | `/monitoring/load-profile`  | `monitoring/load_profile.html`  | `get_load_profile()`, `get_demand_stats()` | ✅ TAMAM |
| **VEE Doğrulama**        | `/monitoring/vee`           | `monitoring/vee.html`           | `get_vee_data()`, `get_vee_corrections()`  | ✅ TAMAM |
| **Eksik Veri Tamamlama** | `/monitoring/missing-data`  | `monitoring/missing-data.html`  | ❌ EKSİK                                   | 🔴 EKSİK |
| **Kayıp/Kaçak Analizi**  | `/monitoring/loss-analysis` | `monitoring/loss_analysis.html` | `get_loss_report()`                        | ✅ TAMAM |

**Eksik Fonksiyonlar:**

- `get_missing_data()` - Eksik veri listesi
- `estimate_missing_data()` - Eksik veri tahmini
- `apply_estimation()` - Tahmini uygulama

---

### 1.4 Faturalama & Tahakkuk Modülü

| Menü Öğesi            | Route                 | Template                    | Database Fonksiyonları                                            | Durum              |
| --------------------- | --------------------- | --------------------------- | ----------------------------------------------------------------- | ------------------ |
| **Tarife Yönetimi**   | `/billing/tariff`     | `billing/tariff.html`       | `get_all_tariffs()`                                               | ✅ TAMAM           |
| **Dönem Açma/Kapama** | `/billing/period`     | `billing/period.html`       | `get_billing_periods_with_stats()`                                | ✅ TAMAM           |
| **Fatura Hesapla**    | `/billing/calculate`  | `billing/calculate.html`    | `get_all_subscribers()`, `get_billing_periods()`, `get_tariffs()` | ⚠️ HESAPLAMA EKSİK |
| **Toplu Fatura Kes**  | `/billing/bulk`       | `billing/bulk-invoice.html` | ❌ EKSİK                                                          | 🔴 EKSİK           |
| **Fatura Önizleme**   | `/billing/preview`    | `billing/preview.html`      | ❌ EKSİK                                                          | 🔴 EKSİK           |
| **Ek Tahakkuk**       | `/billing/additional` | `billing/additional.html`   | ❌ EKSİK                                                          | 🔴 EKSİK           |
| **Fatura İptali**     | `/billing/cancel`     | `billing/cancel.html`       | ❌ EKSİK                                                          | 🔴 EKSİK           |
| **Fatura Yazdır**     | `/billing/print`      | `billing/print.html`        | ❌ EKSİK                                                          | 🔴 EKSİK           |

**Eksik Fonksiyonlar:**

- `calculate_invoice_for_subscriber()` - Tek abone fatura hesaplama (mevcut ama route'da kullanılmıyor)
- `create_invoice()` - Fatura oluşturma
- `bulk_create_invoices()` - Toplu fatura oluşturma
- `get_invoice_preview()` - Fatura önizleme
- `add_additional_charge()` - Ek kalem ekleme
- `cancel_invoice()` - Fatura iptali
- `get_invoice_for_print()` - Yazdırma için fatura verisi

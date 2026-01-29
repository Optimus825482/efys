# EFYS - Hızlı Başlangıç Kılavuzu

**Hedef:** Demo sistemi 1 saatte çalıştır

---

## 🚀 ADIM 1: Database Extensions'ı Entegre Et (10 dk)

### 1.1 services/**init**.py Güncelle

```python
# services/__init__.py
from services.database import *
from services.database_extensions import *

__all__ = [
    # Mevcut fonksiyonlar
    'get_dashboard_stats',
    'get_daily_consumption_chart',
    # ... diğerleri

    # Yeni fonksiyonlar
    'create_invoice',
    'bulk_create_invoices',
    'get_invoice_preview',
    'cancel_invoice',
    'add_additional_charge',
    'create_subscriber',
    'update_subscriber',
    'assign_meter_to_subscriber',
    'get_alarms',
    'get_alarm_stats',
    'get_scheduled_jobs',
    'get_failed_readings',
    'retry_failed_reading',
    'get_missing_data',
    'estimate_missing_data',
    'get_index_report'
]
```

---

## 🚀 ADIM 2: Route Güncellemeleri (20 dk)

### 2.1 routes/billing.py Güncelle

```python
# routes/billing.py - Eklenecek route'lar

from services.database_extensions import (
    create_invoice, bulk_create_invoices,
    get_invoice_preview, cancel_invoice, add_additional_charge
)

@billing_bp.route('/create-invoice', methods=['POST'])
def create_invoice_route():
    """Fatura oluştur"""
    data = request.get_json()
    result = create_invoice(
        data['subscriber_id'],
        data['period_id'],
        data['tariff_id']
    )
    return jsonify(result)

@billing_bp.route('/bulk-create', methods=['POST'])
def bulk_create_route():
    """Toplu fatura oluştur"""
    data = request.get_json()
    result = bulk_create_invoices(data['period_id'])
    return jsonify(result)

@billing_bp.route('/preview/<int:subscriber_id>/<int:period_id>')
def preview_route(subscriber_id, period_id):
    """Fatura önizleme"""
    preview = get_invoice_preview(subscriber_id, period_id)
    return render_template('billing/preview.html', preview=preview)

@billing_bp.route('/cancel/<int:invoice_id>', methods=['POST'])
def cancel_route(invoice_id):
    """Fatura iptali"""
    data = request.get_json()
    result = cancel_invoice(invoice_id, data['reason'])
    return jsonify(result)
```

### 2.2 routes/subscribers.py Güncelle

```python
# routes/subscribers.py - Eklenecek route'lar

from services.database_extensions import (
    create_subscriber, update_subscriber, assign_meter_to_subscriber
)

@subscribers_bp.route('/create', methods=['POST'])
def create_route():
    """Yeni abone oluştur"""
    data = request.get_json()
    result = create_subscriber(data)
    return jsonify(result)

@subscribers_bp.route('/update/<int:id>', methods=['POST'])
def update_route(id):
    """Abone güncelle"""
    data = request.get_json()
    result = update_subscriber(id, data)
    return jsonify(result)

@subscribers_bp.route('/assign-meter', methods=['POST'])
def assign_meter_route():
    """Sayaç atama"""
    data = request.get_json()
    result = assign_meter_to_subscriber(data['meter_id'], data['subscriber_id'])
    return jsonify(result)
```

### 2.3 routes/readings.py Güncelle

```python
# routes/readings.py - Eklenecek route'lar

from services.database_extensions import (
    get_scheduled_jobs, get_failed_readings, retry_failed_reading
)

@readings_bp.route('/scheduled')
def scheduled():
    """Zamanlanmış görevler"""
    jobs = get_scheduled_jobs()
    return render_template('readings/scheduled.html', jobs=jobs)

@readings_bp.route('/failed')
def failed():
    """Başarısız okumalar"""
    failed_readings = get_failed_readings()
    return render_template('readings/failed.html', readings=failed_readings)

@readings_bp.route('/retry/<int:reading_id>', methods=['POST'])
def retry_route(reading_id):
    """Okumayı tekrar dene"""
    result = retry_failed_reading(reading_id)
    return jsonify(result)
```

### 2.4 routes/dashboard.py Güncelle

```python
# routes/dashboard.py - Eklenecek route'lar

from services.database_extensions import get_alarms, get_alarm_stats

@dashboard_bp.route('/alarms')
def alarm_center():
    """Alarm merkezi"""
    alarms = get_alarms(limit=50)
    stats = get_alarm_stats()
    return render_template('dashboard/alarm-center.html', alarms=alarms, stats=stats)
```

---

## 🚀 ADIM 3: Demo Veri Oluştur (15 dk)

### 3.1 scripts/generate_demo_data.py Çalıştır

```bash
cd scripts
python generate_demo_readings.py
```

Bu script zaten mevcut ve çalışıyor. Ek olarak:

### 3.2 Fatura Dönemi Oluştur (SQL)

```sql
-- database/seed_billing_periods.sql
INSERT INTO billing_periods (name, period_start, period_end, invoice_date, due_date, status)
VALUES
('2026 Ocak', '2026-01-01', '2026-01-31', '2026-02-01', '2026-02-15', 'open'),
('2026 Şubat', '2026-02-01', '2026-02-28', '2026-03-01', '2026-03-15', 'open'),
('2026 Mart', '2026-03-01', '2026-03-31', '2026-04-01', '2026-04-15', 'open');
```

Çalıştır:

```bash
psql -U postgres -d osos_db -f database/seed_billing_periods.sql
```

---

## 🚀 ADIM 4: Test Et (15 dk)

### 4.1 Sunucuyu Başlat

```bash
python app.py
```

### 4.2 Test Senaryoları

#### Test 1: Dashboard

```
URL: http://localhost:5000/
Beklenen: KPI kartları, grafikler, alarm listesi görünmeli
```

#### Test 2: Abone Listesi

```
URL: http://localhost:5000/subscribers/list
Beklenen: 30 abone AG-Grid'de görünmeli
```

#### Test 3: Fatura Önizleme

```
URL: http://localhost:5000/billing/preview/1/1
Beklenen: 1 numaralı abone için fatura önizlemesi
```

#### Test 4: Alarm Merkezi

```
URL: http://localhost:5000/alarms
Beklenen: Demo alarmlar görünmeli
```

#### Test 5: Zamanlanmış Görevler

```
URL: http://localhost:5000/readings/scheduled
Beklenen: 3 zamanlanmış görev görünmeli
```

---

## 🚀 ADIM 5: Template Güncellemeleri (Opsiyonel)

### 5.1 templates/dashboard/alarm-center.html Oluştur

```html
{% extends 'base.html' %} {% block title %}Alarm Merkezi{% endblock %} {% block
page_title %}Alarm Merkezi{% endblock %} {% block content %}
<!-- KPI Cards -->
<div class="grid grid-cols-4 gap-4 mb-4">
  <div class="kpi-card">
    <div class="kpi-card-icon danger">🔴</div>
    <div class="kpi-card-value">{{ stats.critical }}</div>
    <div class="kpi-card-label">Kritik Alarmlar</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-card-icon warning">⚠️</div>
    <div class="kpi-card-value">{{ stats.warning }}</div>
    <div class="kpi-card-label">Uyarılar</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-card-icon primary">ℹ️</div>
    <div class="kpi-card-value">{{ stats.info }}</div>
    <div class="kpi-card-label">Bilgilendirme</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-card-icon success">✅</div>
    <div class="kpi-card-value">{{ stats.active }}</div>
    <div class="kpi-card-label">Aktif Alarmlar</div>
  </div>
</div>

<!-- Alarm List -->
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Alarmlar</h3>
  </div>
  <div class="card-body" style="padding: 0">
    <table class="table">
      <thead>
        <tr>
          <th>Önem</th>
          <th>Mesaj</th>
          <th>Zaman</th>
          <th>Durum</th>
        </tr>
      </thead>
      <tbody>
        {% for alarm in alarms %}
        <tr>
          <td>
            <span class="badge badge-{{ alarm.severity }}">
              {{ alarm.severity|upper }}
            </span>
          </td>
          <td>{{ alarm.message }}</td>
          <td>{{ alarm.created_at.strftime('%d.%m.%Y %H:%M') }}</td>
          <td>
            <span
              class="badge badge-{{ 'success' if alarm.status == 'active' else 'secondary' }}"
            >
              {{ alarm.status }}
            </span>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endblock %}
```

---

## ✅ KONTROL LİSTESİ

### Entegrasyon

- [ ] `services/__init__.py` güncellendi
- [ ] `routes/billing.py` güncellendi
- [ ] `routes/subscribers.py` güncellendi
- [ ] `routes/readings.py` güncellendi
- [ ] `routes/dashboard.py` güncellendi

### Demo Veri

- [ ] Okuma verileri oluşturuldu
- [ ] Fatura dönemleri eklendi
- [ ] Aboneler mevcut

### Test

- [ ] Dashboard açılıyor
- [ ] Abone listesi görünüyor
- [ ] Fatura önizleme çalışıyor
- [ ] Alarm merkezi açılıyor
- [ ] Zamanlanmış görevler görünüyor

---

## 🐛 SORUN GİDERME

### Hata: ModuleNotFoundError

```bash
# Çözüm: Paketleri yükle
pip install -r requirements.txt
```

### Hata: Database connection failed

```bash
# Çözüm: PostgreSQL çalışıyor mu kontrol et
pg_ctl status

# Veya
sudo systemctl status postgresql
```

### Hata: Template not found

```bash
# Çözüm: Template dosyası var mı kontrol et
ls templates/dashboard/alarm-center.html
```

### Hata: 500 Internal Server Error

```bash
# Çözüm: Console loglarını kontrol et
# Flask debug mode açık olmalı
export FLASK_ENV=development
python app.py
```

---

## 📞 DESTEK

Sorun yaşarsanız:

1. Console loglarını kontrol edin
2. Database bağlantısını test edin
3. Template dosyalarının varlığını kontrol edin
4. Route'ların doğru import edildiğini kontrol edin

---

**Başarılar! 🚀**

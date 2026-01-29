# 🎯 EFYS - Enerji Faturalandırma ve Yönetim Sistemi

**Proje:** EFYS (OSOS Entegrasyonu)  
**Versiyon:** 1.0  
**Başlangıç:** 29 Ocak 2026  
**Tech Stack:** Python Flask + Vanilla JS + Tailwind CSS + PostgreSQL

---

## 📋 Proje Özeti

OSOS (Otomatik Sayaç Okuma Sistemi) ile entegre çalışan, 15 dakikalık aralıklarla PostgreSQL'e yazılan tüketim verilerini okuyarak işleyen ve faturalayan bir enerji yönetim sistemi.

### Kullanıcı Kararları

| Karar      | Seçim                                 |
| ---------- | ------------------------------------- |
| Tech Stack | Vanilla JS + HTML + Flask             |
| Database   | Mevcut PostgreSQL (aynı DB)           |
| Öncelik    | Dashboard + Faturalama                |
| Tasarım    | Profesyonel, Animasyonsuz, Light Mode |
| Demo Data  | Gerçek PostgreSQL + seed data         |

---

## 🎨 Design System

### Renk Paleti (SaaS Dashboard - Light Mode)

```css
:root {
  /* Primary Colors */
  --color-primary: #2563eb; /* Trust Blue */
  --color-primary-light: #3b82f6;
  --color-primary-dark: #1d4ed8;

  /* Secondary Colors */
  --color-secondary: #60a5fa;

  /* Accent / CTA */
  --color-cta: #f97316; /* Orange */
  --color-cta-hover: #ea580c;

  /* Backgrounds */
  --color-bg-primary: #f8fafc; /* Light Gray */
  --color-bg-white: #ffffff;
  --color-bg-card: #ffffff;

  /* Text */
  --color-text-primary: #1e293b; /* Dark Slate */
  --color-text-secondary: #64748b;
  --color-text-muted: #94a3b8;

  /* Borders */
  --color-border: #e2e8f0;
  --color-border-hover: #cbd5e1;

  /* Status Colors */
  --color-success: #10b981; /* Green */
  --color-warning: #f59e0b; /* Amber */
  --color-danger: #ef4444; /* Red */
  --color-info: #3b82f6; /* Blue */
}
```

### Tipografi

| Element   | Font  | Size | Weight |
| --------- | ----- | ---- | ------ |
| Heading 1 | Inter | 32px | 700    |
| Heading 2 | Inter | 24px | 600    |
| Heading 3 | Inter | 18px | 600    |
| Body      | Inter | 14px | 400    |
| Small     | Inter | 12px | 400    |

### Component Tasarım Kuralları

1. **Cards:** `bg-white`, `border border-gray-200`, `rounded-lg`, `shadow-sm`
2. **Buttons:** `rounded-md`, `font-medium`, `px-4 py-2`
3. **Tables:** `bg-white`, alternating rows, `hover:bg-gray-50`
4. **Inputs:** `border-gray-300`, `focus:ring-blue-500`, `rounded-md`
5. **NO Animations:** Sadece hover state renk değişimi (transition yok)

---

## 📁 Proje Yapısı

```
OSOSDEMO/
├── app.py                      # Flask ana uygulama
├── config.py                   # Konfigürasyon
├── requirements.txt            # Python dependencies
│
├── static/
│   ├── css/
│   │   └── efys.css           # Ana stil dosyası
│   ├── js/
│   │   ├── main.js            # Genel JS
│   │   ├── dashboard.js       # Dashboard özgü
│   │   ├── billing.js         # Faturalama özgü
│   │   └── charts.js          # Chart.js config
│   └── img/
│       └── logo.svg           # EFYS Logo
│
├── templates/
│   ├── base.html              # Layout template
│   ├── components/
│   │   ├── sidebar.html       # Sol menü
│   │   ├── header.html        # Üst bar
│   │   ├── footer.html        # Alt bar
│   │   ├── breadcrumb.html    # Breadcrumb
│   │   ├── card.html          # KPI kartları
│   │   └── table.html         # Data tabloları
│   │
│   ├── dashboard/
│   │   ├── index.html         # Ana dashboard
│   │   ├── live-monitoring.html
│   │   ├── reactive-radar.html
│   │   ├── alarm-center.html
│   │   └── quick-actions.html
│   │
│   ├── billing/               # Faturalama modülü
│   │   ├── index.html         # Faturalama ana
│   │   ├── tariff.html        # Tarife yönetimi
│   │   ├── period.html        # Dönem açma/kapama
│   │   ├── calculate.html     # Fatura hesaplama
│   │   ├── bulk-invoice.html  # Toplu fatura
│   │   ├── preview.html       # Fatura önizleme
│   │   ├── additional.html    # Ek tahakkuk
│   │   ├── cancel.html        # Fatura iptali
│   │   └── print.html         # Yazdır/PDF
│   │
│   ├── readings/              # Okuma işlemleri
│   │   ├── index.html
│   │   ├── instant.html
│   │   ├── scheduled.html
│   │   ├── bulk.html
│   │   ├── history.html
│   │   └── failed.html
│   │
│   ├── monitoring/            # Veri izleme
│   │   ├── index.html
│   │   ├── last-indexes.html
│   │   ├── load-profile.html
│   │   ├── vee.html
│   │   ├── missing-data.html
│   │   └── loss-analysis.html
│   │
│   ├── subscribers/           # Abone yönetimi
│   │   ├── index.html
│   │   ├── card.html
│   │   └── contract.html
│   │
│   ├── reports/               # Raporlama
│   │   ├── index.html
│   │   ├── index-report.html
│   │   ├── consumption.html
│   │   ├── invoice-report.html
│   │   ├── reading-success.html
│   │   ├── loss-report.html
│   │   ├── reactive-report.html
│   │   └── demand-report.html
│   │
│   ├── smart-systems/         # Akıllı sistemler
│   │   ├── index.html
│   │   ├── regulation-bot.html
│   │   ├── penalty-prevention.html
│   │   ├── portal.html
│   │   └── erp-bridge.html
│   │
│   └── settings/              # Sistem ayarları
│       ├── index.html
│       ├── users.html
│       ├── roles.html
│       ├── parameters.html
│       ├── email-sms.html
│       ├── backup.html
│       ├── logs.html
│       ├── api.html
│       ├── integrations.html
│       ├── security.html
│       └── license.html
│
├── models/
│   ├── __init__.py
│   ├── subscriber.py          # Abone modeli
│   ├── meter.py               # Sayaç modeli
│   ├── reading.py             # Okuma modeli
│   ├── invoice.py             # Fatura modeli
│   ├── tariff.py              # Tarife modeli
│   └── user.py                # Kullanıcı modeli
│
├── routes/
│   ├── __init__.py
│   ├── dashboard.py
│   ├── billing.py
│   ├── readings.py
│   ├── monitoring.py
│   ├── subscribers.py
│   ├── reports.py
│   ├── smart_systems.py
│   └── settings.py
│
├── services/
│   ├── __init__.py
│   ├── billing_engine.py      # Fatura hesaplama
│   ├── reactive_calculator.py # Reaktif enerji
│   └── reading_service.py     # Okuma servisi
│
├── seeds/
│   └── demo_data.sql          # Demo veriler
│
└── DOCS/
    ├── EFYS_MENU_STRUCTURE.md
    └── PLAN.md
```

---

## 🗄️ Database Schema (Eklentiler)

Mevcut OSOS tablolarına ek olarak:

```sql
-- Tarife Tablosu
CREATE TABLE tariffs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    t1_price DECIMAL(10,4),        -- Gündüz birim fiyat
    t2_price DECIMAL(10,4),        -- Puant birim fiyat
    t3_price DECIMAL(10,4),        -- Gece birim fiyat
    reactive_price DECIMAL(10,4),  -- Reaktif birim fiyat
    distribution_fee DECIMAL(10,4),
    valid_from DATE,
    valid_to DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fatura Dönemi
CREATE TABLE billing_periods (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),              -- "2026 Ocak"
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'open', -- open, closed, invoiced
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Faturalar
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    invoice_no VARCHAR(20) UNIQUE,
    subscriber_id INTEGER REFERENCES subscribers(id),
    period_id INTEGER REFERENCES billing_periods(id),

    -- Tüketim
    t1_consumption DECIMAL(12,2),
    t2_consumption DECIMAL(12,2),
    t3_consumption DECIMAL(12,2),
    reactive_consumption DECIMAL(12,2),
    total_consumption DECIMAL(12,2),

    -- Tutarlar
    t1_amount DECIMAL(12,2),
    t2_amount DECIMAL(12,2),
    t3_amount DECIMAL(12,2),
    reactive_amount DECIMAL(12,2),
    distribution_amount DECIMAL(12,2),
    additional_charges DECIMAL(12,2) DEFAULT 0,
    discount DECIMAL(12,2) DEFAULT 0,
    subtotal DECIMAL(12,2),
    tax_amount DECIMAL(12,2),
    total_amount DECIMAL(12,2),

    -- Durum
    status VARCHAR(20) DEFAULT 'draft', -- draft, issued, paid, cancelled
    issue_date TIMESTAMP,
    due_date DATE,
    paid_date TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ek Tahakkuklar
CREATE TABLE additional_charges (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER REFERENCES invoices(id),
    description VARCHAR(200),
    amount DECIMAL(12,2),
    charge_type VARCHAR(50), -- penalty, reconnection, misc
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Okuma Görevleri
CREATE TABLE reading_tasks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    schedule_type VARCHAR(20),     -- daily, weekly, monthly, manual
    cron_expression VARCHAR(50),
    meter_group VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    last_run TIMESTAMP,
    next_run TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Menü İzinleri
CREATE TABLE menu_permissions (
    id SERIAL PRIMARY KEY,
    menu_key VARCHAR(50),
    role_id INTEGER REFERENCES roles(id),
    can_view BOOLEAN DEFAULT false,
    can_edit BOOLEAN DEFAULT false,
    can_delete BOOLEAN DEFAULT false
);
```

---

## 🚀 Implementation Fazları

### FAZ 1: Temel Altyapı (Bugün)

- [x] PLAN.md oluşturuldu
- [ ] Proje yapısı (klasörler)
- [ ] Flask app setup
- [ ] Base template + layout
- [ ] Sidebar navigation
- [ ] CSS design system

### FAZ 2: Dashboard + Faturalama Sayfaları (Öncelik)

- [ ] Dashboard ana sayfa
- [ ] Canlı izleme
- [ ] Reaktif radar
- [ ] Alarm merkezi
- [ ] Tarife yönetimi
- [ ] Fatura hesaplama
- [ ] Fatura önizleme

### FAZ 3: Diğer MUST-HAVE Sayfalar

- [ ] Okuma işlemleri (6 sayfa)
- [ ] Veri izleme (6 sayfa)
- [ ] Abone yönetimi (3 sayfa)
- [ ] Raporlama (8 sayfa)
- [ ] Sistem ayarları (10 sayfa)

### FAZ 4: Backend API + Demo Data

- [ ] Flask routes
- [ ] Database models
- [ ] Seed data
- [ ] Billing engine

---

## ✅ Onay Bekleniyor

Erkan, bu plan ile devam edeyim mi?

**EVET** → Sayfaları oluşturmaya başlıyorum  
**HAYIR** → Planda değişiklik yaparım

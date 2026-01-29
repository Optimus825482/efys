# Workflow: Add New Feature

**EFYS - Yeni Özellik Ekleme Adım Adım Kılavuz**

---

## 📋 CHECKLIST

### Phase 1: Planning (30 dakika)
- [ ] Feature gereksinimlerini netleştir
- [ ] Hangi tabloları etkileyeceğini belirle
- [ ] API endpoint'leri planla
- [ ] UI mockup/wireframe oluştur
- [ ] Test senaryolarını listele

### Phase 2: Database (1 saat)
- [ ] Schema değişikliği gerekiyor mu?
- [ ] Migration scripti yaz
- [ ] Test database'de dene
- [ ] Query pattern'lerini belirle

### Phase 3: Backend (2-3 saat)
- [ ] Service methodları yaz
- [ ] Route endpoint'leri ekle
- [ ] Error handling implement et
- [ ] Validation ekle
- [ ] Logging ekle

### Phase 4: Frontend (2-3 saat)
- [ ] Template oluştur
- [ ] Form/input componentleri ekle
- [ ] Chart/table integration
- [ ] API call'ları yap
- [ ] Loading states

### Phase 5: Testing (1 saat)
- [ ] Unit test yaz
- [ ] Manuel test yap
- [ ] Edge case'leri test et
- [ ] Error senaryolarını test et

### Phase 6: Documentation (30 dakika)
- [ ] Kod yorumları ekle
- [ ] README güncelle
- [ ] API dokümanı yaz

---

## 🎯 ÖRNEK: YENİ RAPOR EKLEME

**Feature:** Aylık Karşılaştırma Raporu

### 1. Planning
```
Gereksinim:
- Son 12 ayın tüketim verilerini karşılaştır
- Grafik ile görselleştir
- Excel export özelliği

Tablolar:
- readings (tüketim verileri)
- subscribers (abone bilgileri)

Endpoint:
- GET /reports/comparison
- GET /api/comparison-data
- GET /export/comparison/excel
```

### 2. Database Query
```python
# skills/database.md'den pattern al
def get_comparison_report(self, months=12):
    """Aylık karşılaştırma raporu"""
    self.cur.execute("""
        SELECT 
            TO_CHAR(reading_time, 'YYYY-MM') as period,
            SUM(total_consumption)::int as consumption,
            COUNT(DISTINCT m.subscriber_id) as subscriber_count,
            AVG(power_factor)::numeric as avg_pf
        FROM readings r
        JOIN meters m ON r.meter_id = m.id
        WHERE reading_time >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '%s months')
        GROUP BY TO_CHAR(reading_time, 'YYYY-MM')
        ORDER BY period DESC
    """, (months,))
    return [dict(row) for row in self.cur.fetchall()]
```

### 3. Service Method
```python
# services/database.py (DatabaseService class içine)

def get_comparison_report(self, months=12):
    """Aylık karşılaştırma raporu - YENI EKLENDI"""
    self.cur.execute("""
        SELECT 
            TO_CHAR(reading_time, 'YYYY-MM') as period,
            SUM(total_consumption)::int as consumption,
            COUNT(DISTINCT m.subscriber_id) as subscriber_count
        FROM readings r
        JOIN meters m ON r.meter_id = m.id
        WHERE reading_time >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '%s months')
        GROUP BY TO_CHAR(reading_time, 'YYYY-MM')
        ORDER BY period DESC
    """, (months,))
    return [dict(row) for row in self.cur.fetchall()]
```

### 4. Route Implementation
```python
# routes/reports.py

@reports_bp.route('/comparison')
def comparison():
    """Karşılaştırma raporu - YENI EKLENDI"""
    db = DatabaseService()
    try:
        # Get months from query param
        months = request.args.get('months', 12, type=int)
        
        # Get report data
        report = db.get_comparison_report(months)
        
        # Prepare chart data
        chart_data = {
            'labels': [r['period'] for r in report],
            'values': [r['consumption'] for r in report]
        }
        
        return render_template('reports/comparison.html', 
                             report=report,
                             chart_data=chart_data,
                             months=months)
    except Exception as e:
        print(f"Error loading comparison report: {e}")
        flash('Rapor yüklenemedi', 'error')
        return render_template('reports/comparison.html', 
                             report=None,
                             chart_data=None)
    finally:
        db.close()

@reports_bp.route('/api/comparison-data')
def api_comparison_data():
    """API: Karşılaştırma raporu verisi - YENI EKLENDI"""
    db = DatabaseService()
    try:
        months = request.args.get('months', 12, type=int)
        data = db.get_comparison_report(months)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        db.close()
```

### 5. Template Creation
```html
<!-- templates/reports/comparison.html - YENI DOSYA -->
{% extends 'base.html' %}

{% block title %}Karşılaştırma Raporu{% endblock %}

{% block content %}
<div class="container">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-semibold">Aylık Karşılaştırma Raporu</h1>
        <div class="space-x-2">
            <select id="monthSelect" onchange="changeMonths(this.value)" class="px-3 py-2 border rounded-md">
                <option value="6" {% if months == 6 %}selected{% endif %}>Son 6 Ay</option>
                <option value="12" {% if months == 12 %}selected{% endif %}>Son 12 Ay</option>
                <option value="24" {% if months == 24 %}selected{% endif %}>Son 24 Ay</option>
            </select>
            <a href="/export/comparison/excel" class="btn btn-primary">
                Excel Export
            </a>
        </div>
    </div>

    <!-- Chart -->
    <div class="card mb-6">
        <div class="card-header">
            <h3>Tüketim Trendi</h3>
        </div>
        <div class="card-body">
            <canvas id="comparisonChart" height="300"></canvas>
        </div>
    </div>

    <!-- Data Table -->
    <div class="card">
        <div class="card-header">
            <h3>Detay Veriler</h3>
        </div>
        <div class="card-body p-0">
            <table class="w-full">
                <thead>
                    <tr>
                        <th>Dönem</th>
                        <th>Tüketim (kWh)</th>
                        <th>Abone Sayısı</th>
                        <th>Değişim</th>
                    </tr>
                </thead>
                <tbody>
                    {% if report %}
                        {% for row in report %}
                        <tr>
                            <td>{{ row.period }}</td>
                            <td>{{ "{:,}".format(row.consumption).replace(',', '.') }}</td>
                            <td>{{ row.subscriber_count }}</td>
                            <td>
                                {% if loop.index < report|length %}
                                    {% set prev = report[loop.index] %}
                                    {% set change = ((row.consumption - prev.consumption) / prev.consumption * 100)|round(1) %}
                                    <span class="{% if change > 0 %}text-green-600{% else %}text-red-600{% endif %}">
                                        {{ "%+.1f"|format(change) }}%
                                    </span>
                                {% else %}
                                    -
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr>
                            <td colspan="4" class="text-center">Veri bulunamadı</td>
                        </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1"></script>
<script>
{% if chart_data %}
const ctx = document.getElementById('comparisonChart').getContext('2d');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: {{ chart_data.labels | tojson }},
        datasets: [{
            label: 'Tüketim (kWh)',
            data: {{ chart_data.values | tojson }},
            borderColor: '#2563EB',
            backgroundColor: 'rgba(37, 99, 235, 0.1)',
            tension: 0.4,
            fill: true
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: value => value.toLocaleString('tr-TR') + ' kWh'
                }
            }
        }
    }
});
{% endif %}

function changeMonths(months) {
    window.location.href = `/reports/comparison?months=${months}`;
}
</script>
{% endblock %}
```

### 6. Link Ekle (reports/index.html)
```html
<!-- Existing cards... -->

<!-- YENI KART EKLE -->
<a href="{{ url_for('reports.comparison') }}" class="card" style="cursor: pointer">
    <div class="card-body" style="text-align: center; padding: 24px">
        <div style="...">
            <!-- Icon -->
        </div>
        <div style="font-weight: 600; color: var(--color-text-primary)">
            Karşılaştırma Raporu
        </div>
        <div style="font-size: 0.875rem; color: var(--color-text-secondary)">
            Dönemsel karşılaştırma
        </div>
    </div>
</a>
```

### 7. Test
```bash
# Manuel test
1. http://localhost:5000/reports/comparison açın
2. Sayfa yükleniyor mu kontrol edin
3. Chart render oluyor mu?
4. Dropdown ile ay değişimi çalışıyor mu?
5. Excel export linki var mı?

# API test
curl http://localhost:5000/api/comparison-data?months=12
# Response: {"success": true, "data": [...]}
```

---

## 🔍 TROUBLESHOOTING

### Template Render Hatası
```python
# Error: KeyError: 'key_name'
# Çözüm: Template'te defensive access
{{ data.get('key_name', 'default_value') }}

# veya
{% if data and data.key_name %}
    {{ data.key_name }}
{% endif %}
```

### Database Query Hatası
```python
# Error: relation "table_name" does not exist
# Çözüm: Tablo adını kontrol et, schema uygula
python scripts/apply_schema.py

# Error: column "col_name" does not exist
# Çözüm: Migration yap
ALTER TABLE table_name ADD COLUMN col_name TYPE;
```

### 500 Server Error
```python
# Check terminal output for error
# Common causes:
1. Undefined route reference in template
2. Database connection error
3. Missing template file
4. Python syntax error

# Debug:
python -c "from routes.reports import comparison; print('OK')"
```

---

## ✅ COMPLETION CHECKLIST

Feature tamamlandı mı?
- [ ] Sayfa açılıyor
- [ ] Veri görüntüleniyor
- [ ] Chart çalışıyor
- [ ] Error handling çalışıyor (DB bağlantısı koparsa ne olur?)
- [ ] Loading state var mı?
- [ ] Responsive (mobilde çalışıyor mu?)
- [ ] Export fonksiyonu çalışıyor
- [ ] Kod yorumlandı
- [ ] Test edildi

---

**Süre Tahmini:** 4-6 saat (deneyimli developer)  
**Son Güncelleme:** 29 Ocak 2026

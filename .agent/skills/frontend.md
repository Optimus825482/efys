# Frontend Skills

**EFYS - Templates, Charts & Client-side Integration**

---

## 🎨 Template Patterns

### Pattern 1: Base Layout Extension
```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}EFYS{% endblock %}</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- AG-Grid -->
    <script src="https://cdn.jsdelivr.net/npm/ag-grid-community@31.0.0/dist/ag-grid-community.min.js"></script>
    {% block head %}{% endblock %}
</head>
<body>
    {% include 'components/header.html' %}
    {% include 'components/sidebar.html' %}
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    {% include 'components/footer.html' %}
    {% block scripts %}{% endblock %}
</body>
</html>

<!-- templates/feature/page.html -->
{% extends 'base.html' %}

{% block title %}Feature Page{% endblock %}

{% block content %}
    <h1>{{ page_title }}</h1>
    <!-- Content here -->
{% endblock %}

{% block scripts %}
<script>
    // Page-specific JS
</script>
{% endblock %}
```

### Pattern 2: Component Include
```html
<!-- templates/components/kpi_card.html -->
<div class="kpi-card">
    <div class="kpi-card-icon {{ icon_class }}">
        {{ icon_svg | safe }}
    </div>
    <div class="kpi-card-value">{{ value }}</div>
    <div class="kpi-card-label">{{ label }}</div>
    <div class="kpi-card-change {{ 'negative' if change < 0 else 'positive' }}">
        {{ change }}
    </div>
</div>

<!-- Usage in page -->
{% include 'components/kpi_card.html' with context
    value=stats.total_consumption,
    label='Toplam Tüketim',
    change='+5.2%',
    icon_class='primary'
%}
```

### Pattern 3: Conditional Rendering
```html
{% if data %}
    <table>
        {% for item in data %}
            <tr>
                <td>{{ item.name }}</td>
                <td>{{ item.value }}</td>
            </tr>
        {% endfor %}
    </table>
{% else %}
    <div class="empty-state">
        <p>Veri bulunamadı</p>
    </div>
{% endif %}
```

---

## 📊 Chart Integration

### Pattern 1: Chart.js - Line Chart
```html
<div class="card">
    <div class="card-header">
        <h3>Tüketim Trendi</h3>
    </div>
    <div class="card-body">
        <canvas id="trendChart" height="300"></canvas>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1"></script>
<script>
const ctx = document.getElementById('trendChart').getContext('2d');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: {{ chart_data.labels | tojson }},  // ['2026-01-01', '2026-01-02', ...]
        datasets: [{
            label: 'Tüketim (kWh)',
            data: {{ chart_data.values | tojson }},  // [1234, 1456, ...]
            borderColor: '#2563EB',
            backgroundColor: 'rgba(37, 99, 235, 0.1)',
            tension: 0.4,
            fill: true
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top'
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return value.toLocaleString('tr-TR') + ' kWh';
                    }
                }
            }
        }
    }
});
</script>
```

### Pattern 2: ECharts - Gauge
```html
<div id="gaugeChart" style="width: 100%; height: 400px;"></div>

<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<script>
const chart = echarts.init(document.getElementById('gaugeChart'));
const option = {
    series: [{
        type: 'gauge',
        min: 0,
        max: 1,
        splitNumber: 10,
        axisLine: {
            lineStyle: {
                color: [
                    [0.85, '#EF4444'],  // Red
                    [0.90, '#F59E0B'],  // Yellow
                    [1, '#10B981']       // Green
                ],
                width: 30
            }
        },
        detail: {
            formatter: function(value) {
                return (value * 100).toFixed(1) + '%';
            },
            fontSize: 30
        },
        data: [{
            value: {{ reactive.ortalama_cos_phi }},
            name: 'Güç Faktörü'
        }]
    }]
};
chart.setOption(option);

// Responsive
window.addEventListener('resize', () => chart.resize());
</script>
```

### Pattern 3: Google Charts - Gauge (Alternative)
```html
<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
<div id="gaugeChart"></div>

<script>
google.charts.load('current', {'packages':['gauge']});
google.charts.setOnLoadCallback(drawGauge);

function drawGauge() {
    const data = google.visualization.arrayToDataTable([
        ['Label', 'Value'],
        ['Cos φ', {{ reactive.ortalama_cos_phi }}]
    ]);

    const options = {
        width: 400,
        height: 300,
        min: 0.7,
        max: 1.0,
        greenFrom: 0.90,
        greenTo: 1.0,
        yellowFrom: 0.85,
        yellowTo: 0.90,
        redFrom: 0.70,
        redTo: 0.85
    };

    const chart = new google.visualization.Gauge(document.getElementById('gaugeChart'));
    chart.draw(data, options);
}
</script>
```

---

## 📋 AG-Grid Integration

### Pattern 1: Basic Grid
```html
<div id="dataGrid" style="height: 500px;" class="ag-theme-alpine"></div>

<script>
const columnDefs = [
    { field: 'subscriber_code', headerName: 'Abone Kodu', sortable: true, filter: true },
    { field: 'name', headerName: 'İsim', sortable: true, filter: true },
    { field: 'sector', headerName: 'Sektör', sortable: true, filter: true },
    { 
        field: 'avg_daily_kwh', 
        headerName: 'Ort. Tüketim',
        sortable: true,
        filter: 'agNumberColumnFilter',
        valueFormatter: params => params.value ? params.value.toLocaleString('tr-TR') + ' kWh' : '-'
    }
];

const gridOptions = {
    columnDefs: columnDefs,
    rowData: {{ subscribers | tojson }},  // Pass from backend
    defaultColDef: {
        resizable: true,
        sortable: true,
        filter: true
    },
    pagination: true,
    paginationPageSize: 25,
    domLayout: 'normal'
};

const gridDiv = document.querySelector('#dataGrid');
new agGrid.Grid(gridDiv, gridOptions);
</script>
```

### Pattern 2: Grid with Actions
```html
<script>
const columnDefs = [
    { field: 'id', headerName: 'ID', hide: true },
    { field: 'name', headerName: 'İsim' },
    { field: 'status', headerName: 'Durum',
        cellRenderer: params => {
            const status = params.value;
            const badge = status === 'Aktif' ? 'badge-success' : 'badge-danger';
            return `<span class="badge ${badge}">${status}</span>`;
        }
    },
    { 
        headerName: 'İşlemler',
        cellRenderer: params => {
            const id = params.data.id;
            return `
                <a href="/subscribers/${id}" class="btn btn-sm btn-primary">Görüntüle</a>
                <button onclick="deleteItem(${id})" class="btn btn-sm btn-danger">Sil</button>
            `;
        }
    }
];

function deleteItem(id) {
    if (confirm('Silmek istediğinizden emin misiniz?')) {
        fetch(`/api/subscribers/${id}`, { method: 'DELETE' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Hata: ' + data.error);
                }
            });
    }
}
</script>
```

---

## 🔄 API Integration

### Pattern 1: Fetch API - GET
```javascript
// Get data from API endpoint
fetch('/api/data')
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            updateChart(data.data);
        } else {
            showError(data.error);
        }
    })
    .catch(error => {
        console.error('API Error:', error);
        showError('Veri yüklenemedi');
    });
```

### Pattern 2: Fetch API - POST
```javascript
// Send form data
const formData = {
    name: document.getElementById('name').value,
    value: document.getElementById('value').value
};

fetch('/api/create', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(formData)
})
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Başarıyla oluşturuldu');
            location.href = `/detail/${data.data.id}`;
        } else {
            showError(data.error);
        }
    })
    .catch(error => {
        showError('İşlem başarısız');
    });
```

### Pattern 3: Real-time Data Update
```javascript
// Auto-refresh data every 30 seconds
let chartInstance;

function updateChart(data) {
    if (chartInstance) {
        chartInstance.data.labels = data.labels;
        chartInstance.data.datasets[0].data = data.values;
        chartInstance.update();
    }
}

function fetchLatestData() {
    fetch('/api/latest')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                updateChart(data.data);
            }
        })
        .catch(error => console.error('Update failed:', error));
}

// Auto-refresh
setInterval(fetchLatestData, 30000);  // 30 seconds
```

---

## 🎨 Styling Patterns (Tailwind)

### Pattern 1: Card Component
```html
<div class="bg-white rounded-lg shadow-md p-6">
    <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-900">Card Title</h3>
        <button class="text-blue-600 hover:text-blue-800">Action</button>
    </div>
    <div class="space-y-2">
        <!-- Content -->
    </div>
</div>
```

### Pattern 2: Form with Validation
```html
<form class="space-y-4" onsubmit="handleSubmit(event)">
    <div>
        <label for="name" class="block text-sm font-medium text-gray-700 mb-1">
            İsim <span class="text-red-500">*</span>
        </label>
        <input 
            type="text" 
            id="name" 
            name="name"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
        <span class="text-red-500 text-sm hidden" id="name-error">Bu alan zorunludur</span>
    </div>
    
    <button 
        type="submit"
        class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
    >
        Kaydet
    </button>
</form>

<script>
function handleSubmit(event) {
    event.preventDefault();
    
    const name = document.getElementById('name').value;
    if (!name.trim()) {
        document.getElementById('name-error').classList.remove('hidden');
        return;
    }
    
    // Submit form
    event.target.submit();
}
</script>
```

### Pattern 3: Alert Messages
```html
<!-- Success -->
<div class="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg flex items-center">
    <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
        <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"/>
    </svg>
    <span>İşlem başarılı</span>
</div>

<!-- Error -->
<div class="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg flex items-center">
    <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
        <path d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"/>
    </svg>
    <span>Hata oluştu</span>
</div>
```

---

## 🔄 Dynamic Content Updates

### Pattern 1: Search/Filter
```html
<input 
    type="text" 
    id="searchInput" 
    placeholder="Ara..." 
    onkeyup="filterTable()"
    class="px-3 py-2 border rounded-md"
>

<table id="dataTable">
    <tbody>
        {% for item in data %}
        <tr>
            <td>{{ item.name }}</td>
            <td>{{ item.value }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<script>
function filterTable() {
    const input = document.getElementById('searchInput');
    const filter = input.value.toLowerCase();
    const table = document.getElementById('dataTable');
    const rows = table.getElementsByTagName('tr');
    
    for (let i = 0; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        let found = false;
        
        for (let j = 0; j < cells.length; j++) {
            const cell = cells[j];
            if (cell.textContent.toLowerCase().indexOf(filter) > -1) {
                found = true;
                break;
            }
        }
        
        rows[i].style.display = found ? '' : 'none';
    }
}
</script>
```

### Pattern 2: Modal Dialog
```html
<!-- Modal Trigger -->
<button onclick="openModal('myModal')">Aç</button>

<!-- Modal -->
<div id="myModal" class="fixed inset-0 bg-black bg-opacity-50 hidden items-center justify-center">
    <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold">Modal Başlık</h3>
            <button onclick="closeModal('myModal')" class="text-gray-500 hover:text-gray-700">
                ✕
            </button>
        </div>
        <div class="mb-4">
            Modal içeriği
        </div>
        <div class="flex justify-end space-x-2">
            <button onclick="closeModal('myModal')" class="px-4 py-2 border rounded-md">
                İptal
            </button>
            <button class="px-4 py-2 bg-blue-600 text-white rounded-md">
                Tamam
            </button>
        </div>
    </div>
</div>

<script>
function openModal(id) {
    document.getElementById(id).classList.remove('hidden');
    document.getElementById(id).classList.add('flex');
}

function closeModal(id) {
    document.getElementById(id).classList.add('hidden');
    document.getElementById(id).classList.remove('flex');
}
</script>
```

---

## 🎯 Performance Optimization

### Pattern 1: Lazy Loading Images
```html
<img 
    data-src="/static/images/large.jpg" 
    alt="Image" 
    class="lazy-load"
    src="/static/images/placeholder.jpg"
>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const lazyImages = document.querySelectorAll('.lazy-load');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy-load');
                imageObserver.unobserve(img);
            }
        });
    });
    
    lazyImages.forEach(img => imageObserver.observe(img));
});
</script>
```

### Pattern 2: Debounce for Search
```javascript
// Prevent excessive API calls
let debounceTimer;

function debounceSearch(query) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        performSearch(query);
    }, 500);  // Wait 500ms after typing stops
}

document.getElementById('searchInput').addEventListener('input', (e) => {
    debounceSearch(e.target.value);
});
```

---

**Son Güncelleme:** 29 Ocak 2026  
**Libraries:** Chart.js 4.4, AG-Grid 31, ECharts 5.5, Tailwind CSS

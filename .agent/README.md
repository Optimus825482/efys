# EFYS Agent Skills Repository

**Tarih:** 29 Ocak 2026  
**Proje:** EFYS - Enerji Faturalandırma ve Yönetim Sistemi  
**Amaç:** Yeniden kullanılabilir kod pattern'leri ve best practices

---

## 📁 Dizin Yapısı

```
.agent/
├── README.md                    # Bu dosya
├── skills/                      # Kategorize edilmiş skill'ler
│   ├── database.md             # DB operations, queries, migrations
│   ├── backend.md              # Route, service, error handling
│   ├── frontend.md             # Template, chart, API integration
│   ├── testing.md              # Test patterns, fixtures
│   └── security.md             # Auth, validation, encryption
├── templates/                   # Code templates
│   ├── route_template.py
│   ├── service_template.py
│   └── test_template.py
└── workflows/                   # Multi-step workflows
    ├── add_new_feature.md
    ├── fix_bug.md
    └── refactor_service.md
```

---

## 🎯 Kullanım

### Yeni Feature Eklerken
1. `workflows/add_new_feature.md` - Adım adım checklist
2. `skills/database.md` - Query pattern'leri
3. `skills/backend.md` - Route & service implementasyonu
4. `templates/route_template.py` - Boilerplate kod

### Bug Fix
1. `workflows/fix_bug.md` - Debug stratejisi
2. `skills/backend.md` - Error handling pattern'leri
3. `skills/testing.md` - Test case'leri

### Refactoring
1. `workflows/refactor_service.md` - Refactoring checklist
2. `skills/backend.md` - Service separation pattern'leri

---

## 🔧 Quick Reference

### Database Query
```python
# skills/database.md → Basic Query Pattern
from services.database import get_db, get_cursor

with get_db() as conn:
    cur = get_cursor(conn)
    cur.execute("SELECT * FROM table WHERE id = %s", (id,))
    return cur.fetchone()
```

### Route Implementation
```python
# skills/backend.md → Route Pattern
from services.database import DatabaseService

@bp.route('/endpoint')
def endpoint():
    db = DatabaseService()
    try:
        data = db.get_data()
        return render_template('page.html', data=data)
    except Exception as e:
        print(f"Error: {e}")
        return render_template('page.html', data=[])
    finally:
        db.close()
```

### API Endpoint
```python
# skills/backend.md → API Pattern
@bp.route('/api/data')
def api_data():
    try:
        data = get_data()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

---

## 📚 Skill Kategorileri

| Kategori | Dosya | İçerik |
|----------|-------|--------|
| **Database** | `skills/database.md` | Connection pooling, query optimization, migrations |
| **Backend** | `skills/backend.md` | Routes, services, error handling, logging |
| **Frontend** | `skills/frontend.md` | Templates, charts, forms, API calls |
| **Testing** | `skills/testing.md` | Unit tests, integration tests, fixtures |
| **Security** | `skills/security.md` | Authentication, validation, encryption |

---

## 🚀 Örnekler

### Scenario 1: Yeni Rapor Ekle
```bash
1. workflows/add_new_feature.md - 7 adımlı checklist
2. skills/database.md → "Report Query Pattern" kopyala
3. templates/route_template.py → Boilerplate oluştur
4. skills/frontend.md → Chart integration örneği
5. Test yaz ve doğrula
```

### Scenario 2: 500 Error Fix
```bash
1. workflows/fix_bug.md - Debug stratejisi
2. skills/backend.md → "Error Handling" pattern'ini uygula
3. skills/testing.md → Test case ekle
4. Verify fix
```

---

**Güncelleme:** Her yeni pattern keşfedildiğinde ilgili skill dosyasına ekle.

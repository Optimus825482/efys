# Backend Skills

**EFYS - Flask Routes, Services & Error Handling**

---

## 🛣️ Route Patterns

### Pattern 1: Page Render with Data
```python
from flask import Blueprint, render_template
from services.database import DatabaseService

bp = Blueprint('feature', __name__)

@bp.route('/')
def index():
    """Feature ana sayfası"""
    db = DatabaseService()
    try:
        # Get data from database
        stats = db.get_stats()
        items = db.get_items()
        
        return render_template('feature/index.html', 
                             stats=stats, 
                             items=items)
    except Exception as e:
        # Log error
        print(f"Error loading feature index: {e}")
        return render_template('feature/index.html', 
                             stats=None, 
                             items=[])
    finally:
        db.close()  # ⚠️ ALWAYS close
```

### Pattern 2: API Endpoint (JSON Response)
```python
from flask import jsonify

@bp.route('/api/data')
def api_data():
    """API: JSON data endpoint"""
    db = DatabaseService()
    try:
        data = db.get_data()
        return jsonify({
            'success': True,
            'data': data,
            'meta': {'count': len(data)}
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()
```

### Pattern 3: POST with Validation
```python
from flask import request, flash, redirect, url_for

@bp.route('/create', methods=['POST'])
def create():
    """Create new item"""
    # Get form data
    name = request.form.get('name')
    value = request.form.get('value')
    
    # Validate
    if not name or not value:
        flash('Tüm alanlar zorunludur', 'error')
        return redirect(url_for('feature.index'))
    
    db = DatabaseService()
    try:
        # Create in database
        item_id = db.create_item(name, value)
        flash(f'Başarıyla oluşturuldu (ID: {item_id})', 'success')
        return redirect(url_for('feature.detail', id=item_id))
    except Exception as e:
        flash(f'Hata: {str(e)}', 'error')
        return redirect(url_for('feature.index'))
    finally:
        db.close()
```

### Pattern 4: Dynamic Route with Parameter
```python
@bp.route('/<int:id>')
def detail(id):
    """Detail page with ID parameter"""
    db = DatabaseService()
    try:
        item = db.get_item_by_id(id)
        
        if not item:
            return render_template('errors/404.html'), 404
        
        # Get related data
        related = db.get_related_items(id)
        
        return render_template('feature/detail.html', 
                             item=item, 
                             related=related)
    except Exception as e:
        print(f"Error loading detail: {e}")
        return render_template('errors/500.html'), 500
    finally:
        db.close()
```

---

## 🔧 Service Layer Patterns

### Pattern 1: Database Service Method
```python
# services/database.py

class DatabaseService:
    def get_feature_report(self, start_date=None, end_date=None):
        """Feature raporu"""
        # Set defaults
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # Query
        self.cur.execute("""
            SELECT 
                DATE(created_at) as tarih,
                COUNT(*) as total,
                SUM(amount) as sum_amount
            FROM feature_table
            WHERE created_at BETWEEN %s AND %s
            GROUP BY DATE(created_at)
            ORDER BY tarih
        """, (start_date, end_date))
        
        # Return as dict list
        return [dict(row) for row in self.cur.fetchall()]
```

### Pattern 2: Transactional Operation
```python
def create_complex_item(data):
    """Multiple table insert with transaction"""
    with get_db() as conn:
        cur = get_cursor(conn)
        
        try:
            # Insert main record
            cur.execute("""
                INSERT INTO main_table (name, value)
                VALUES (%s, %s)
                RETURNING id
            """, (data['name'], data['value']))
            main_id = cur.fetchone()['id']
            
            # Insert related records
            for detail in data['details']:
                cur.execute("""
                    INSERT INTO detail_table (main_id, detail_value)
                    VALUES (%s, %s)
                """, (main_id, detail))
            
            conn.commit()
            return main_id
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Transaction failed: {e}")
```

### Pattern 3: Bulk Operations
```python
from psycopg2.extras import execute_values

def bulk_create_items(items):
    """Batch insert for performance"""
    with get_db() as conn:
        cur = get_cursor(conn)
        
        # Prepare data tuples
        data = [(item['name'], item['value']) for item in items]
        
        # Bulk insert (FAST)
        execute_values(cur, """
            INSERT INTO items (name, value)
            VALUES %s
        """, data)
        
        return len(data)
```

---

## 🚨 Error Handling

### Pattern 1: Specific Exception Handling
```python
import psycopg2

@bp.route('/data')
def get_data():
    db = DatabaseService()
    try:
        data = db.get_data()
        return render_template('page.html', data=data)
        
    except psycopg2.OperationalError as e:
        # Database connection error
        log_to_db('ERROR', 'Database', f'Connection failed: {e}')
        flash('Veritabanı bağlantısı kurulamadı', 'error')
        return render_template('page.html', data=[]), 503
        
    except psycopg2.IntegrityError as e:
        # Unique constraint, foreign key violation
        log_to_db('ERROR', 'Database', f'Integrity error: {e}')
        flash('Veri tutarsızlığı', 'error')
        return render_template('page.html', data=[]), 400
        
    except ValueError as e:
        # Data validation error
        flash(f'Geçersiz veri: {e}', 'error')
        return redirect(url_for('index'))
        
    except Exception as e:
        # Unexpected error
        log_to_db('ERROR', 'Feature', f'Unexpected: {e}')
        flash('Beklenmeyen hata oluştu', 'error')
        return render_template('page.html', data=[]), 500
        
    finally:
        db.close()
```

### Pattern 2: Global Error Handler
```python
# app.py

from flask import render_template

@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    log_to_db('ERROR', 'Server', str(e))
    return render_template('errors/500.html'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    # Log all unhandled exceptions
    log_to_db('CRITICAL', 'Unhandled', str(e))
    return render_template('errors/500.html'), 500
```

### Pattern 3: API Error Response
```python
def api_error_response(error_code, message, status_code=400):
    """Standardized API error response"""
    return jsonify({
        'success': False,
        'error': {
            'code': error_code,
            'message': message
        }
    }), status_code

# Usage
@bp.route('/api/create', methods=['POST'])
def api_create():
    data = request.get_json()
    
    if not data or 'name' not in data:
        return api_error_response('VALIDATION_ERROR', 'name gerekli', 400)
    
    try:
        result = create_item(data)
        return jsonify({'success': True, 'data': result})
    except IntegrityError:
        return api_error_response('DUPLICATE', 'Bu kayıt zaten mevcut', 409)
    except Exception as e:
        return api_error_response('INTERNAL_ERROR', str(e), 500)
```

---

## 📝 Logging System

### Pattern 1: Database Logger
```python
# services/logger.py

from services.database import get_db, get_cursor
from datetime import datetime

def log_to_db(level, module, message, user_id=None):
    """System logs tablosuna yaz"""
    try:
        with get_db() as conn:
            cur = get_cursor(conn)
            cur.execute("""
                INSERT INTO system_logs (log_level, module, message, user_id)
                VALUES (%s, %s, %s, %s)
            """, (level, module, message, user_id))
    except Exception as e:
        # Fallback to file if DB fails
        with open('logs/fallback.log', 'a') as f:
            f.write(f"[{datetime.now()}] {level} - {module}: {message}\n")
            f.write(f"[DB LOG FAILED]: {e}\n")

# Usage in routes
from services.logger import log_to_db

@bp.route('/action')
def action():
    try:
        result = perform_action()
        log_to_db('INFO', 'Feature', f'Action completed: {result}')
        return jsonify({'success': True})
    except Exception as e:
        log_to_db('ERROR', 'Feature', f'Action failed: {e}')
        return jsonify({'success': False}), 500
```

### Pattern 2: Request Logger Decorator
```python
from functools import wraps
from flask import request

def log_request(func):
    """Log all requests to this endpoint"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Log request
        log_to_db('INFO', 'Request', 
                 f"{request.method} {request.path} from {request.remote_addr}")
        
        # Execute function
        try:
            result = func(*args, **kwargs)
            log_to_db('INFO', 'Response', f"{request.path} - Success")
            return result
        except Exception as e:
            log_to_db('ERROR', 'Response', f"{request.path} - Error: {e}")
            raise
    
    return wrapper

# Usage
@bp.route('/critical')
@log_request
def critical_endpoint():
    return jsonify({'data': 'sensitive'})
```

---

## 🔐 Validation & Security

### Pattern 1: Input Validation
```python
from decimal import Decimal, InvalidOperation

def validate_invoice_data(data):
    """Validate invoice creation data"""
    errors = []
    
    # Required fields
    if not data.get('subscriber_id'):
        errors.append('subscriber_id gerekli')
    
    if not data.get('period_id'):
        errors.append('period_id gerekli')
    
    # Type validation
    try:
        subscriber_id = int(data['subscriber_id'])
    except (ValueError, TypeError):
        errors.append('subscriber_id sayı olmalı')
    
    # Range validation
    amount = data.get('amount', 0)
    try:
        amount = Decimal(str(amount))
        if amount < 0:
            errors.append('amount negatif olamaz')
    except InvalidOperation:
        errors.append('amount geçersiz')
    
    if errors:
        raise ValueError('; '.join(errors))
    
    return True

# Usage
@bp.route('/create', methods=['POST'])
def create():
    data = request.form.to_dict()
    try:
        validate_invoice_data(data)
        # Proceed with creation
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('index'))
```

### Pattern 2: CSRF Protection
```python
# Install: pip install flask-wtf

from flask_wtf import CSRFProtect

csrf = CSRFProtect(app)

# In templates
<form method="POST">
    {{ csrf_token() }}
    <!-- form fields -->
</form>

# Exempt API endpoints
@bp.route('/api/public', methods=['POST'])
@csrf.exempt
def public_api():
    return jsonify({'data': 'public'})
```

---

## 📊 Report Generation Patterns

### Pattern 1: Simple Report
```python
@bp.route('/report')
def consumption_report():
    """Tüketim raporu"""
    db = DatabaseService()
    try:
        # Get date range from query params
        start_date = request.args.get('start', default_start)
        end_date = request.args.get('end', default_end)
        
        # Generate report
        report = db.get_consumption_report(start_date, end_date)
        
        return render_template('reports/consumption.html', 
                             report=report,
                             start_date=start_date,
                             end_date=end_date)
    except Exception as e:
        flash(f'Rapor oluşturulamadı: {e}', 'error')
        return render_template('reports/consumption.html', report=None)
    finally:
        db.close()
```

### Pattern 2: Excel Export
```python
from flask import send_file
import openpyxl
from datetime import datetime
import os

@bp.route('/export/excel')
def export_excel():
    """Excel export"""
    db = DatabaseService()
    try:
        data = db.get_report_data()
        
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Rapor"
        
        # Headers
        ws.append(['Abone Kodu', 'İsim', 'Tüketim', 'Tutar'])
        
        # Data
        for row in data:
            ws.append([row['code'], row['name'], row['consumption'], row['amount']])
        
        # Save to temp file
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join('temp', filename)
        wb.save(filepath)
        
        return send_file(filepath, 
                        as_attachment=True,
                        download_name=filename,
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        flash(f'Excel export hatası: {e}', 'error')
        return redirect(url_for('reports.index'))
    finally:
        db.close()
```

---

## 🎯 Best Practices Checklist

### Route Implementation
- [ ] Blueprint kullanıldı mı?
- [ ] DatabaseService her zaman `finally` bloğunda kapatılıyor mu?
- [ ] Error handling var mı?
- [ ] Logging yapılıyor mu?
- [ ] Input validation yapıldı mı?
- [ ] Boş data durumu handle ediliyor mu?

### Service Method
- [ ] Tek bir iş yapıyor mu? (SRP)
- [ ] Parameterized query kullanılıyor mu?
- [ ] Transaction gerekiyorsa commit/rollback var mı?
- [ ] Return type tutarlı mı? (dict, list, None)
- [ ] Docstring yazıldı mı?

### API Endpoint
- [ ] Consistent response format (success, data, error)
- [ ] HTTP status code doğru mu?
- [ ] CORS gerekiyorsa ayarlandı mı?
- [ ] Rate limiting var mı?
- [ ] Authentication check var mı?

---

## 🔄 Refactoring Patterns

### Before: God Class
```python
# services/database.py (1225 lines)
class DatabaseService:
    def get_subscribers(self): ...
    def get_readings(self): ...
    def get_invoices(self): ...
    def get_tariffs(self): ...
    # ... 50+ methods
```

### After: Separated Services
```python
# services/subscriber_service.py
class SubscriberService:
    def get_all(self): ...
    def get_by_id(self, id): ...
    def create(self, data): ...
    def update(self, id, data): ...

# services/reading_service.py
class ReadingService:
    def get_latest(self, limit): ...
    def get_by_meter(self, meter_id): ...
    def create_bulk(self, readings): ...

# Usage
from services.subscriber_service import SubscriberService
from services.reading_service import ReadingService

sub_service = SubscriberService()
read_service = ReadingService()
```

---

**Son Güncelleme:** 29 Ocak 2026  
**Framework:** Flask 3.0

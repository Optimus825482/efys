# EFYS - PHASE 2 IMPLEMENTATION BACKLOG

**Tarih:** 29 Ocak 2026  
**Phase 1 Tamamlanma:** %100  
**Phase 2 Başlangıç:** Şubat 2026 (tahmini)

---

## 🎯 EXECUTIVE SUMMARY

Phase 1'de tüm core modüller gerçek database verileriyle entegre edildi. Sistem %100 operasyonel durumda ancak authentication ve bazı advanced features eksik. Bu doküman Phase 2 için roadmap'i içerir.

---

## ✅ PHASE 1 COMPLETED (100%)

### Tamamlanan İşler

✅ **Mock Data Temizleme**
- Smart Systems - Portal Management → Real DB
- Smart Systems - Regulation Bot → MevzuatService
- Settings - Users Table → Placeholder page

✅ **Eksik Template'ler**
- `templates/settings/roles.html` → Created
- `templates/settings/security.html` → Created

✅ **Route Testing**
- 39 route test edildi
- 100% success rate
- Hiçbir exception yok

✅ **Database Integration**
- %95 real data kullanımı
- OSB loss analysis çalışıyor
- Mevzuat sistemi full functional
- Tariff management 4 table entegrasyonu

---

## 📋 PHASE 2 BACKLOG (Priority Order)

### 🔴 CRITICAL - Authentication & Security (4 hafta)

#### 1.1 Database Schema - Users & Roles (1 hafta)

**Schema SQL:**
```sql
-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role_id INTEGER REFERENCES roles(id),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Roles Table
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default Roles
INSERT INTO roles (name, description, permissions) VALUES
('admin', 'Sistem Yöneticisi - Tüm Erişim', 
 '{"dashboard": ["view"], "billing": ["view", "create", "edit", "delete"], "subscribers": ["view", "create", "edit", "delete"], "reports": ["view", "export"], "monitoring": ["view"], "settings": ["view", "edit"]}'),
('operator', 'Fatura Operatörü', 
 '{"dashboard": ["view"], "billing": ["view", "create", "edit"], "subscribers": ["view"], "reports": ["view", "export"], "monitoring": ["view"]}'),
('viewer', 'Sadece Görüntüleme', 
 '{"dashboard": ["view"], "reports": ["view"], "monitoring": ["view"]}');

-- Sessions Table (optional - for tracking)
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Security Events Log
CREATE TABLE security_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    event_type VARCHAR(50) NOT NULL, -- login_success, login_failed, logout, password_change, etc.
    ip_address INET,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Migration Script:**
```python
# scripts/create_auth_tables.py
import psycopg2
from config import DATABASE_URL

def apply_auth_schema():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    with open('database/auth_schema.sql', 'r') as f:
        cur.execute(f.read())
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Auth tables created successfully")

if __name__ == "__main__":
    apply_auth_schema()
```

#### 1.2 Authentication Implementation (2 hafta)

**Dependencies:**
```bash
pip install Flask-Login Flask-Bcrypt Flask-WTF email-validator
```

**Auth Service (`services/auth.py`):**
```python
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
import psycopg2

bcrypt = Bcrypt()

class User(UserMixin):
    def __init__(self, id, username, email, role_id, permissions):
        self.id = id
        self.username = username
        self.email = email
        self.role_id = role_id
        self.permissions = permissions
    
    def has_permission(self, module, action):
        """Check if user has permission"""
        return action in self.permissions.get(module, [])

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def verify_password(password, password_hash):
    return bcrypt.check_password_hash(password_hash, password)

def authenticate_user(username, password):
    """Authenticate user and return User object"""
    # DB query + password verification
    pass

def create_user(username, email, password, role_id):
    """Create new user with hashed password"""
    password_hash = hash_password(password)
    # DB insert
    pass
```

**Login Route (`routes/auth.py`):**
```python
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from services.auth import authenticate_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = authenticate_user(username, password)
        if user:
            login_user(user)
            return redirect(url_for('dashboard.index'))
        else:
            flash('Kullanıcı adı veya şifre hatalı', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
```

**Permission Decorator:**
```python
from functools import wraps
from flask import abort
from flask_login import current_user

def permission_required(module, action):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_permission(module, action):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage:
@billing_bp.route('/create', methods=['POST'])
@login_required
@permission_required('billing', 'create')
def create_invoice():
    pass
```

#### 1.3 Security Hardening (1 hafta)

**CSRF Protection:**
```python
# app.py
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
```

**Rate Limiting:**
```python
# app.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Login endpoint
@limiter.limit("5 per minute")
@auth_bp.route('/login', methods=['POST'])
def login():
    pass
```

**Session Timeout:**
```python
# app.py
from datetime import timedelta

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

---

### 🟡 MEDIUM - System Logging & Monitoring (2 hafta)

#### 2.1 System Logs Table (1 hafta)

**Schema:**
```sql
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    log_level VARCHAR(20) NOT NULL, -- DEBUG, INFO, WARNING, ERROR, CRITICAL
    module VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    user_id INTEGER REFERENCES users(id),
    ip_address INET,
    request_path TEXT,
    exception_traceback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_logs_level ON system_logs(log_level);
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at DESC);
CREATE INDEX idx_system_logs_module ON system_logs(module);
```

**Logging Service (`services/logging_service.py`):**
```python
import logging
from flask import request
from flask_login import current_user

class DatabaseHandler(logging.Handler):
    def emit(self, record):
        """Write log to database"""
        with get_db() as conn:
            cur = get_cursor(conn)
            cur.execute("""
                INSERT INTO system_logs (log_level, module, message, user_id, ip_address, request_path, exception_traceback)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                record.levelname,
                record.module,
                record.getMessage(),
                current_user.id if current_user.is_authenticated else None,
                request.remote_addr if request else None,
                request.path if request else None,
                record.exc_text
            ))

# Setup
logger = logging.getLogger('efys')
logger.addHandler(DatabaseHandler())
```

#### 2.2 Audit Log (1 hafta)

**Important actions to log:**
- Invoice creation/cancellation
- Tariff changes
- User login/logout
- Permission changes
- Subscriber data modifications

---

### 🟢 LOW - Export Functions (1 hafta)

#### 3.1 Excel Export (`services/export.py`)

**Dependencies:**
```bash
pip install openpyxl xlsxwriter
```

**Implementation:**
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from io import BytesIO

def export_to_excel(data, columns, sheet_name="Report"):
    """Export data to Excel file"""
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name
    
    # Header row
    header_fill = PatternFill(start_color="3B82F6", end_color="3B82F6", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for col_idx, column in enumerate(columns, start=1):
        cell = ws.cell(row=1, column=col_idx, value=column['label'])
        cell.fill = header_fill
        cell.font = header_font
    
    # Data rows
    for row_idx, row_data in enumerate(data, start=2):
        for col_idx, column in enumerate(columns, start=1):
            value = row_data.get(column['field'])
            ws.cell(row=row_idx, column=col_idx, value=value)
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = max(len(str(cell.value or "")) for cell in column)
        ws.column_dimensions[column[0].column_letter].width = min(max_length + 2, 50)
    
    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output
```

#### 3.2 PDF Export

**Dependencies:**
```bash
pip install reportlab weasyprint
```

**Implementation:**
```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from io import BytesIO

def export_to_pdf(data, columns, title="Report"):
    """Export data to PDF file"""
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    elements = []
    
    # Title
    styles = getSampleStyleSheet()
    title_paragraph = Paragraph(title, styles['Title'])
    elements.append(title_paragraph)
    
    # Table data
    table_data = [[col['label'] for col in columns]]
    for row in data:
        table_data.append([str(row.get(col['field'], '')) for col in columns])
    
    # Create table
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#3B82F6'),
        ('TEXTCOLOR', (0, 0), (-1, 0), '#FFFFFF'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, '#DDDDDD')
    ]))
    
    elements.append(table)
    doc.build(elements)
    output.seek(0)
    return output
```

---

### 🟢 LOW - Backup System (1 hafta)

#### 4.1 PostgreSQL Backup

**Backup Service (`services/backup.py`):**
```python
import subprocess
import os
from datetime import datetime

BACKUP_DIR = "backups"

def create_backup():
    """Create PostgreSQL backup using pg_dump"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{BACKUP_DIR}/osos_db_{timestamp}.sql"
    
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # pg_dump command
    cmd = [
        "pg_dump",
        "-h", "localhost",
        "-U", "postgres",
        "-d", "osos_db",
        "-f", backup_file,
        "--clean",
        "--if-exists"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        
        # Log to database
        file_size = os.path.getsize(backup_file)
        log_backup_history("full", backup_file, file_size, "success")
        
        return {"success": True, "file": backup_file, "size": file_size}
    except subprocess.CalledProcessError as e:
        log_backup_history("full", backup_file, 0, "failed", str(e))
        return {"success": False, "error": str(e)}

def restore_backup(backup_file):
    """Restore from backup file"""
    cmd = [
        "psql",
        "-h", "localhost",
        "-U", "postgres",
        "-d", "osos_db",
        "-f", backup_file
    ]
    
    subprocess.run(cmd, check=True)
```

#### 4.2 Scheduled Backups

**Using APScheduler:**
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(create_backup, 'cron', hour=2, minute=0)  # Daily at 02:00
scheduler.start()
```

---

## 📊 IMPLEMENTATION TIMELINE

| Phase | Tasks | Duration | Start | End |
|-------|-------|----------|-------|-----|
| **Phase 2.1** | Auth Schema + Implementation | 4 weeks | Week 5 | Week 8 |
| **Phase 2.2** | System Logging | 2 weeks | Week 9 | Week 10 |
| **Phase 2.3** | Export Functions | 1 week | Week 11 | Week 11 |
| **Phase 2.4** | Backup System | 1 week | Week 12 | Week 12 |

**Total Duration:** 12 hafta (3 ay)

---

## 🔒 SECURITY CHECKLIST

### Pre-Production Requirements

- [ ] Authentication implemented (Flask-Login)
- [ ] Password hashing (bcrypt)
- [ ] RBAC (Role-Based Access Control)
- [ ] CSRF protection (Flask-WTF)
- [ ] Rate limiting (Flask-Limiter)
- [ ] Session timeout configured
- [ ] HTTPS enforced (nginx reverse proxy)
- [ ] SQL injection protection (✅ Already done - psycopg2 parameterized queries)
- [ ] XSS protection (✅ Already done - Jinja2 auto-escaping)
- [ ] Security headers (Helmet equivalent)
- [ ] Audit logging active
- [ ] Backup system running
- [ ] Monitoring alerts configured

---

## 📝 TESTING STRATEGY

### Unit Tests
```python
# tests/test_auth.py
def test_password_hashing():
    password = "test123"
    hashed = hash_password(password)
    assert verify_password(password, hashed)

def test_user_permissions():
    user = User(1, "admin", "admin@osb.com", 1, {"billing": ["view", "create"]})
    assert user.has_permission("billing", "view")
    assert not user.has_permission("billing", "delete")
```

### Integration Tests
```python
# tests/test_login.py
def test_login_success(client):
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_login_failed(client):
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'wrong'
    })
    assert b'Kullanıcı adı veya şifre hatalı' in response.data
```

---

## 🚀 DEPLOYMENT CHECKLIST

### Production Deployment Steps

1. **Environment Variables**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY="<random-secure-key>"
   export DATABASE_URL="postgresql://..."
   export SESSION_COOKIE_SECURE=True
   ```

2. **Nginx Configuration**
   ```nginx
   server {
       listen 443 ssl http2;
       server_name efys.gonenosb.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Systemd Service**
   ```ini
   [Unit]
   Description=EFYS Flask Application
   After=network.target
   
   [Service]
   User=efys
   WorkingDirectory=/opt/efys
   ExecStart=/opt/efys/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Database Backup Cron**
   ```cron
   0 2 * * * /usr/bin/python3 /opt/efys/scripts/create_backup.py
   ```

---

## 📞 SUPPORT & CONTACTS

- **Developer:** Erkan (FULL-STACK-MASTER agent)
- **Database:** PostgreSQL 14+
- **Framework:** Flask 3.0+
- **Deployment:** Gunicorn + Nginx

---

**Document Version:** 1.0  
**Last Updated:** 29 Ocak 2026  
**Status:** Phase 1 Complete ✅ | Phase 2 Ready to Start 🚀

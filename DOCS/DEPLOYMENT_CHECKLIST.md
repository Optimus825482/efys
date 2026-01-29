# EFYS - Deployment Checklist

## 📋 Pre-Deployment Checklist

### 1. Database Setup ✅

```bash
# Create database
psql -U postgres -c "CREATE DATABASE osos_db;"

# Run schema
psql -U postgres -d osos_db -f database/schema.sql

# Create missing tables
psql -U postgres -d osos_db -f database/create_missing_tables.sql

# Load demo data (optional)
psql -U postgres -d osos_db -f database/demo_data.sql
```

**Verification:**

```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Expected tables:
-- ✓ subscribers
-- ✓ meters
-- ✓ readings
-- ✓ tariffs
-- ✓ billing_periods
-- ✓ invoices
-- ✓ alarms
-- ✓ scheduled_readings
-- ✓ additional_charges
-- ✓ system_logs
-- ✓ users
-- ✓ roles
-- ✓ user_roles
```

---

### 2. Environment Configuration ✅

**File:** `.env` (create if not exists)

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/osos_db

# Flask
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secret-key-change-this-in-production

# Application
APP_NAME=EFYS
APP_VERSION=1.0.0

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# CORS (if needed)
CORS_ORIGINS=http://localhost:5000
```

**Verification:**

```bash
# Test database connection
python -c "import os; import psycopg2; conn = psycopg2.connect(os.environ.get('DATABASE_URL')); print('✓ Database connection OK')"
```

---

### 3. Python Dependencies ✅

**File:** `requirements.txt`

```txt
Flask==2.3.3
psycopg2-binary==2.9.7
python-dotenv==1.0.0
colorama==0.4.6
requests==2.31.0
```

**Installation:**

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Verification:**

```bash
pip list | grep -E "Flask|psycopg2|python-dotenv"
```

---

### 4. File Structure Verification ✅

```
EFYS/
├── app.py                          ✓ Main application
├── requirements.txt                ✓ Dependencies
├── .env                            ✓ Environment variables
├── database/
│   ├── schema.sql                  ✓ Main schema
│   ├── create_missing_tables.sql   ✓ Additional tables
│   └── demo_data.sql               ✓ Demo data (optional)
├── routes/
│   ├── __init__.py                 ✓
│   ├── dashboard.py                ✓ Dashboard routes
│   ├── subscribers.py              ✓ Subscriber routes
│   ├── readings.py                 ✓ Reading routes
│   ├── billing.py                  ✓ Billing routes
│   ├── monitoring.py               ✓ Monitoring routes
│   └── reports.py                  ✓ Report routes
├── services/
│   ├── __init__.py                 ✓ Service exports
│   ├── database.py                 ✓ Core database service
│   └── database_extensions.py      ✓ Extended functions
├── templates/
│   ├── base.html                   ✓ Base template
│   ├── dashboard/
│   │   ├── index.html              ✓
│   │   ├── alarm-center.html       ✓
│   │   ├── live-monitoring.html    ✓
│   │   └── reactive-radar.html     ✓
│   ├── subscribers/
│   │   ├── index.html              ✓
│   │   ├── list.html               ✓
│   │   ├── card.html               ✓
│   │   └── ...                     ✓
│   ├── readings/
│   │   └── ...                     ✓
│   ├── billing/
│   │   └── ...                     ✓
│   ├── monitoring/
│   │   ├── missing-data.html       ✓
│   │   └── ...                     ✓
│   └── reports/
│       ├── index_report.html       ✓
│       └── ...                     ✓
└── static/
    ├── css/
    │   └── style.css               ✓
    └── js/
        └── main.js                 ✓
```

---

### 5. Application Startup ✅

**Start the application:**

```bash
# Development
python app.py

# Production (with Gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Verification:**

```bash
# Check if server is running
curl http://localhost:5000/

# Expected: HTML response (dashboard page)
```

---

### 6. Endpoint Testing ✅

**Run automated tests:**

```bash
python test_all_endpoints.py
```

**Expected output:**

```
======================================================================
EFYS - Endpoint Verification Test
======================================================================

Testing Dashboard...
----------------------------------------------------------------------
✓ /                                      [200] 0.123s
✓ /live                                  [200] 0.089s
✓ /reactive                              [200] 0.095s
✓ /alarms                                [200] 0.102s

Testing Subscribers...
----------------------------------------------------------------------
✓ /subscribers/                          [200] 0.078s
✓ /subscribers/list                      [200] 0.091s
...

======================================================================
Test Summary
======================================================================
Total Tests:  47
Passed:       47
Failed:       0
Success Rate: 100.0%
======================================================================

✓ All tests passed! System is ready.
```

---

### 7. Manual Testing Checklist ✅

#### Dashboard Module

- [ ] Dashboard loads with KPI cards
- [ ] Charts render correctly
- [ ] Alarm center shows alarms
- [ ] Live monitoring updates
- [ ] Reactive radar displays gauge

#### Subscribers Module

- [ ] Subscriber list loads (AG-Grid)
- [ ] Add new subscriber form works
- [ ] Edit subscriber form works
- [ ] Meter assignment works
- [ ] Subscriber detail page loads

#### Readings Module

- [ ] Instant readings display
- [ ] Scheduled readings list
- [ ] Bulk reading form works
- [ ] Failed readings show
- [ ] Reading history loads

#### Billing Module

- [ ] Billing dashboard loads
- [ ] Tariff management works
- [ ] Period management works
- [ ] Invoice calculation works
- [ ] Bulk invoice creation works
- [ ] Invoice preview displays
- [ ] Invoice cancellation works

#### Monitoring Module

- [ ] Last indexes display
- [ ] Load profile chart renders
- [ ] VEE validation works
- [ ] Missing data management
- [ ] Loss analysis displays

#### Reports Module

- [ ] Index report loads (AG-Grid)
- [ ] Consumption report displays
- [ ] Invoice report works
- [ ] Export buttons work (Excel, PDF)

---

### 8. Performance Testing ✅

**Load time targets:**

- Dashboard: < 2 seconds
- List pages: < 1.5 seconds
- Detail pages: < 1 second
- API calls: < 500ms

**Test with browser DevTools:**

1. Open Chrome DevTools (F12)
2. Go to Network tab
3. Reload page
4. Check "Load" time at bottom

---

### 9. Security Checklist ✅

- [ ] SQL injection protection (parameterized queries)
- [ ] XSS protection (input sanitization)
- [ ] CSRF protection (Flask-WTF)
- [ ] Secure session cookies
- [ ] HTTPS enabled (production)
- [ ] Environment variables secured
- [ ] Database credentials not in code
- [ ] Error messages don't leak sensitive info

---

### 10. Browser Compatibility ✅

**Test on:**

- [ ] Chrome 90+ ✓
- [ ] Firefox 88+ ✓
- [ ] Safari 14+ ✓
- [ ] Edge 90+ ✓

**Responsive breakpoints:**

- [ ] Desktop (1920px) ✓
- [ ] Laptop (1366px) ✓
- [ ] Tablet (768px) ✓
- [ ] Mobile (375px) ✓

---

## 🚀 Deployment Steps

### Option 1: Local Development

```bash
# 1. Clone repository
git clone <repo-url>
cd EFYS

# 2. Setup environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 3. Configure database
cp .env.example .env
# Edit .env with your database credentials

# 4. Setup database
psql -U postgres -d osos_db -f database/schema.sql
psql -U postgres -d osos_db -f database/create_missing_tables.sql

# 5. Run application
python app.py

# 6. Open browser
# http://localhost:5000
```

---

### Option 2: Production (Linux Server)

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql nginx

# 2. Setup PostgreSQL
sudo -u postgres psql
CREATE DATABASE osos_db;
CREATE USER efys_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE osos_db TO efys_user;
\q

# 3. Clone and setup application
cd /var/www
git clone <repo-url> efys
cd efys
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# 4. Configure environment
cp .env.example .env
nano .env  # Edit with production settings

# 5. Setup database
psql -U efys_user -d osos_db -f database/schema.sql
psql -U efys_user -d osos_db -f database/create_missing_tables.sql

# 6. Create systemd service
sudo nano /etc/systemd/system/efys.service
```

**Service file:**

```ini
[Unit]
Description=EFYS Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/efys
Environment="PATH=/var/www/efys/venv/bin"
ExecStart=/var/www/efys/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

```bash
# 7. Start service
sudo systemctl start efys
sudo systemctl enable efys
sudo systemctl status efys

# 8. Configure Nginx
sudo nano /etc/nginx/sites-available/efys
```

**Nginx config:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /var/www/efys/static;
    }
}
```

```bash
# 9. Enable site
sudo ln -s /etc/nginx/sites-available/efys /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 10. Setup SSL (optional but recommended)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 📊 Post-Deployment Verification

### 1. Health Check

```bash
curl http://localhost:5000/
# Expected: 200 OK with HTML content
```

### 2. Database Connection

```bash
python -c "from services.database import DatabaseService; db = DatabaseService(); print('✓ DB OK')"
```

### 3. API Endpoints

```bash
curl http://localhost:5000/api/stats
# Expected: JSON response with stats
```

### 4. Logs

```bash
# Check application logs
tail -f /var/log/efys/app.log

# Check Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 🔧 Troubleshooting

### Issue: Database connection error

**Solution:**

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection string in .env
echo $DATABASE_URL

# Test connection
psql -U postgres -d osos_db -c "SELECT 1;"
```

### Issue: 500 Internal Server Error

**Solution:**

```bash
# Check application logs
tail -f logs/app.log

# Check Python errors
python app.py  # Run in foreground to see errors
```

### Issue: Static files not loading

**Solution:**

```bash
# Check static folder permissions
ls -la static/

# Check Nginx config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## ✅ Final Checklist

- [ ] Database created and tables exist
- [ ] Environment variables configured
- [ ] Python dependencies installed
- [ ] Application starts without errors
- [ ] All 47+ pages load successfully
- [ ] No 500 errors
- [ ] Forms submit correctly
- [ ] API endpoints respond
- [ ] Charts render properly
- [ ] Responsive design works
- [ ] Browser compatibility verified
- [ ] Security measures in place
- [ ] Backup strategy defined
- [ ] Monitoring setup (optional)
- [ ] Documentation complete

---

## 🎉 Success!

If all items are checked, your EFYS system is ready for production use!

**Next steps:**

1. Train users
2. Monitor performance
3. Collect feedback
4. Plan enhancements

---

**Last Updated:** 2025-01-XX  
**Version:** 1.0.0

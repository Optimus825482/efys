# Database Skills

**EFYS - PostgreSQL Operations & Best Practices**

---

## 🔌 Connection Management

### Pattern 1: Context Manager (Önerilen)
```python
from services.database import get_db, get_cursor

with get_db() as conn:
    cur = get_cursor(conn)  # RealDictCursor - returns dict
    cur.execute("SELECT * FROM subscribers WHERE id = %s", (id,))
    result = cur.fetchone()
    return dict(result) if result else None
```

### Pattern 2: DatabaseService Class
```python
from services.database import DatabaseService

db = DatabaseService()
try:
    result = db.get_data()
    return result
except Exception as e:
    log_error(str(e))
    raise
finally:
    db.close()  # ⚠️ ZORUNLU
```

### Pattern 3: Connection Pooling (Production)
```python
from psycopg2 import pool

connection_pool = pool.SimpleConnectionPool(
    minconn=5,
    maxconn=20,
    dsn=DATABASE_URL
)

@contextmanager
def get_db():
    conn = connection_pool.getconn()
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        connection_pool.putconn(conn)
```

---

## 📊 Query Patterns

### SELECT - Basic
```python
# Single row
cur.execute("SELECT * FROM subscribers WHERE id = %s", (id,))
subscriber = cur.fetchone()

# Multiple rows
cur.execute("SELECT * FROM subscribers WHERE status = %s", ('Aktif',))
subscribers = cur.fetchall()

# With pagination
cur.execute("""
    SELECT * FROM subscribers 
    ORDER BY subscriber_code 
    LIMIT %s OFFSET %s
""", (per_page, offset))
```

### SELECT - Complex (JOIN, Aggregation)
```python
# JOIN example
cur.execute("""
    SELECT 
        s.id, s.name, s.subscriber_code,
        m.meter_no, m.status as meter_status,
        t.name as tariff_name
    FROM subscribers s
    LEFT JOIN meters m ON s.id = m.subscriber_id
    LEFT JOIN tariffs t ON s.tariff_id = t.id
    WHERE s.status = %s
    ORDER BY s.subscriber_code
""", ('Aktif',))

# Aggregation with GROUP BY
cur.execute("""
    SELECT 
        s.sector,
        COUNT(*) as subscriber_count,
        SUM(s.contract_demand) as total_demand
    FROM subscribers s
    WHERE s.status = 'Aktif'
    GROUP BY s.sector
    ORDER BY subscriber_count DESC
""")

# Date range filtering
cur.execute("""
    SELECT 
        DATE(reading_time) as tarih,
        SUM(total_consumption) as tuketim
    FROM readings
    WHERE reading_time BETWEEN %s AND %s
    GROUP BY DATE(reading_time)
    ORDER BY tarih
""", (start_date, end_date))
```

### INSERT - Single & Bulk
```python
# Single insert
cur.execute("""
    INSERT INTO subscribers (subscriber_code, name, sector, status)
    VALUES (%s, %s, %s, %s)
    RETURNING id
""", (code, name, sector, status))
new_id = cur.fetchone()['id']

# Bulk insert (FAST)
from psycopg2.extras import execute_values

data = [
    ('A-000001', 'Firma 1', 'Kimya'),
    ('A-000002', 'Firma 2', 'Gıda'),
    # ... 1000'lerce satır
]

execute_values(cur, """
    INSERT INTO subscribers (subscriber_code, name, sector)
    VALUES %s
""", data)
```

### UPDATE & DELETE
```python
# UPDATE
cur.execute("""
    UPDATE subscribers 
    SET status = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id = %s
""", ('Askıda', subscriber_id))

# DELETE (soft delete preferred)
cur.execute("""
    UPDATE subscribers 
    SET status = 'Kapalı', deleted_at = CURRENT_TIMESTAMP
    WHERE id = %s
""", (subscriber_id,))

# Hard delete (dikkatli kullan)
cur.execute("DELETE FROM readings WHERE meter_id = %s", (meter_id,))
```

---

## 🚀 Performance Optimization

### Index Strategy
```sql
-- Time-based queries
CREATE INDEX idx_readings_time ON readings(reading_time);

-- Foreign key queries
CREATE INDEX idx_readings_meter ON readings(meter_id);

-- Composite index (multi-column)
CREATE INDEX idx_readings_meter_time ON readings(meter_id, reading_time);

-- Partial index (filtered)
CREATE INDEX idx_alarms_unack ON alarms(acknowledged) 
WHERE acknowledged = false;

-- Full-text search
CREATE INDEX idx_subscribers_name ON subscribers USING GIN(to_tsvector('turkish', name));
```

### Query Optimization
```python
# ❌ N+1 Problem
subscribers = db.get_subscribers()  # 30 rows
for sub in subscribers:
    meter = db.get_meter(sub['id'])  # 30 separate queries! BAD

# ✅ JOIN ile tek query
cur.execute("""
    SELECT 
        s.*,
        m.meter_no,
        m.status as meter_status
    FROM subscribers s
    LEFT JOIN meters m ON s.id = m.subscriber_id
""")
subscribers = cur.fetchall()  # 1 query, 30 rows
```

### EXPLAIN ANALYZE
```python
# Query performance analizi
cur.execute("""
    EXPLAIN ANALYZE
    SELECT * FROM readings 
    WHERE meter_id = 1 
    AND reading_time >= '2026-01-01'
""")
plan = cur.fetchall()
print(plan)  # Execution time, index usage
```

---

## 📈 Report Queries

### Consumption Report
```python
cur.execute("""
    SELECT 
        s.subscriber_code,
        s.name,
        SUM(r.total_consumption)::int as total_kwh,
        AVG(r.power_factor)::numeric as avg_pf
    FROM readings r
    JOIN meters m ON r.meter_id = m.id
    JOIN subscribers s ON m.subscriber_id = s.id
    WHERE r.reading_time >= %s AND r.reading_time < %s
    GROUP BY s.id, s.subscriber_code, s.name
    ORDER BY total_kwh DESC
""", (start_date, end_date))
```

### Invoice Report
```python
cur.execute("""
    SELECT 
        bp.name as period,
        COUNT(i.id) as invoice_count,
        SUM(i.total_amount) as total_amount,
        SUM(CASE WHEN i.status = 'paid' THEN i.total_amount ELSE 0 END) as paid_amount
    FROM billing_periods bp
    LEFT JOIN invoices i ON i.period_id = bp.id
    GROUP BY bp.id, bp.name
    ORDER BY bp.period_start DESC
""")
```

### Loss Analysis
```python
cur.execute("""
    WITH meter_consumption AS (
        SELECT 
            DATE_TRUNC('month', reading_time) as month,
            SUM(total_consumption) as meter_total
        FROM readings
        GROUP BY DATE_TRUNC('month', reading_time)
    ),
    billed_consumption AS (
        SELECT 
            DATE_TRUNC('month', i.issue_date) as month,
            SUM(i.total_consumption) as billed_total
        FROM invoices i
        GROUP BY DATE_TRUNC('month', i.issue_date)
    )
    SELECT 
        mc.month,
        mc.meter_total,
        bc.billed_total,
        (mc.meter_total - bc.billed_total) as loss,
        ROUND((mc.meter_total - bc.billed_total) / mc.meter_total * 100, 2) as loss_percent
    FROM meter_consumption mc
    LEFT JOIN billed_consumption bc ON mc.month = bc.month
    ORDER BY mc.month DESC
""")
```

---

## 🔒 Security Best Practices

### SQL Injection Prevention
```python
# ✅ Parameterized query (SAFE)
cur.execute("SELECT * FROM subscribers WHERE name = %s", (user_input,))

# ❌ String concatenation (DANGEROUS)
cur.execute(f"SELECT * FROM subscribers WHERE name = '{user_input}'")
# user_input = "'; DROP TABLE subscribers; --" → SQL INJECTION!
```

### Input Validation
```python
from decimal import Decimal, InvalidOperation

def safe_decimal(value):
    """Güvenli decimal conversion"""
    try:
        return Decimal(str(value))
    except (ValueError, InvalidOperation):
        raise ValueError(f"Invalid decimal: {value}")

# Usage
amount = safe_decimal(request.form.get('amount'))
```

---

## 🧪 Testing Database Operations

### Setup Test Database
```python
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Create test DB
conn = psycopg2.connect(dbname='postgres', user='postgres', password='...')
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()
cur.execute('DROP DATABASE IF EXISTS osos_test')
cur.execute('CREATE DATABASE osos_test')

# Apply schema
with open('database/schema.sql') as f:
    schema = f.read()
    test_conn = psycopg2.connect(dbname='osos_test', ...)
    test_conn.cursor().execute(schema)
```

### Fixture Data
```python
def insert_test_subscribers():
    """Test için sample data"""
    with get_db() as conn:
        cur = get_cursor(conn)
        cur.execute("""
            INSERT INTO subscribers (subscriber_code, name, sector, status)
            VALUES 
                ('TEST-001', 'Test Firma 1', 'Kimya', 'Aktif'),
                ('TEST-002', 'Test Firma 2', 'Gıda', 'Aktif')
        """)
```

---

## 🛠️ Migration Strategy

### Version Control with Alembic
```bash
# Install
pip install alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Manual Migration Script
```python
# migrations/001_add_column.py
def upgrade():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            ALTER TABLE subscribers 
            ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE
        """)

def downgrade():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("ALTER TABLE subscribers DROP COLUMN IF EXISTS email_verified")
```

---

## 📝 Logging & Monitoring

### Log Database Operations
```python
def log_to_db(level, module, message, user_id=None):
    """System logs tablosuna kaydet"""
    with get_db() as conn:
        cur = get_cursor(conn)
        cur.execute("""
            INSERT INTO system_logs (log_level, module, message, user_id)
            VALUES (%s, %s, %s, %s)
        """, (level, module, message, user_id))

# Usage
log_to_db('INFO', 'Billing', f'Invoice {invoice_id} created', user_id=1)
log_to_db('ERROR', 'Database', f'Query failed: {error}')
```

### Query Performance Monitoring
```python
import time

def timed_query(query, params=None):
    """Query execution time ölç"""
    start = time.time()
    with get_db() as conn:
        cur = get_cursor(conn)
        cur.execute(query, params)
        result = cur.fetchall()
    duration = time.time() - start
    
    if duration > 1.0:  # 1 saniyeden uzun
        log_to_db('WARN', 'Performance', f'Slow query: {duration:.2f}s')
    
    return result
```

---

## 🎯 Common Pitfalls

### ❌ Connection Leak
```python
# BAD - connection never closed
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
result = cur.fetchall()
return result  # Connection leak!
```

### ❌ Uncommitted Transaction
```python
# BAD - changes not saved
with get_db() as conn:
    cur = conn.cursor()
    cur.execute("UPDATE ...")
    # Missing conn.commit()!
```

### ❌ Incorrect Exception Handling
```python
# BAD - swallows specific errors
try:
    result = db.query()
except:  # Catches everything, including KeyboardInterrupt!
    pass
```

---

**Son Güncelleme:** 29 Ocak 2026  
**Referans:** PostgreSQL 14, psycopg2 2.9

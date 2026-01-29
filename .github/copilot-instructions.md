# EFYS Coding Guide

Flask energy billing system for Gönen OSB processing 15-minute meter readings. **Stack:** Python 3.10+ | Flask 3.0 | PostgreSQL | psycopg2 | Jinja2 | Vanilla JS

## Critical Architecture Rules

### 1. Raw SQL Only - No ORM
SQLAlchemy is **intentionally disabled**. All database logic uses raw psycopg2 in `services/database.py` or `services/database_extensions.py`:

```python
# Always use context manager + RealDictCursor
with get_db() as conn:
    cur = get_cursor(conn)  # Returns dict rows
    cur.execute("SELECT * FROM subscribers WHERE id = %s", (id,))
    return cur.fetchone()
```

### 2. Service Layer Separation
Routes (`routes/*.py`) **never** execute SQL directly. Always call methods from `services/database.py`:

```python
# ✅ In routes/billing.py
db = DatabaseService()
try:
    invoices = db.get_invoices_by_period(period_id)
    return render_template('billing/index.html', invoices=invoices)
finally:
    db.close()  # Always close in finally block
```

### 3. Turkish-English Hybrid
- **Database:** Turkish names (`aboneler`, `faturalar`, `get_fatura_hesapla`)
- **Code:** English comments and docstrings
- **Subscriber codes:** Format `A-000001` (zero-padded 6 digits)

## Domain Knowledge

### EPDK Time Periods (Turkey Electricity)
Readings are split by time-of-use tariffs:
- **T1 (Gündüz/Day):** 06:00-17:00
- **T2 (Puant/Peak):** 17:00-22:00  
- **T3 (Gece/Night):** 22:00-06:00

See `scripts/generate_demo_readings.py::get_time_period()` for implementation.

### Billing Flow
Invoice calculation in `services/database.py::calculate_invoice()`:
1. Aggregate 15-min `readings` for billing period
2. Split consumption into T1/T2/T3 buckets
3. Apply `tariffs` table rates (energy + demand charges)
4. Calculate reactive power penalty if cos φ < 0.9
5. Add ÖTV + KDV taxes (EPDK regulations)

**Key:** Demand charges use `max_demand` from readings, not `contract_demand` from subscriber.

## Development Commands

```bash
# Run dev server
python app.py  # http://localhost:5000

# Database setup
python scripts/apply_schema.py
python scripts/generate_demo_readings.py  # Creates Jan 1-29, 2026 data

# Test endpoints
python test_all_endpoints.py
```

## Blueprint Structure

Routes organized by domain (see `routes/__init__.py`):
- Dashboard: `/` (no prefix)
- Billing: `/billing/*`
- Readings: `/readings/*`
- Monitoring: `/monitoring/*`
- Subscribers: `/subscribers/*`
- Reports: `/reports/*`

Add new features:
1. Create `routes/feature.py` with blueprint
2. Register in `routes/__init__.py::register_blueprints()`
3. Add database methods to `services/database.py`
4. Create Jinja2 templates in `templates/feature/`

## Frontend Stack

- **Tables:** AG-Grid 31.0.0 (loaded in `templates/base.html`)
- **Charts:** ECharts 5.5.0 + Google Charts for gauges
- **No frameworks:** Vanilla JS only
- **Style:** Tailwind CSS, Plus Jakarta Sans font, no animations

## Common Issues

1. `"No module named 'flask_sqlalchemy'"` → Expected, ORM is disabled
2. Connection pool errors → Ensure `db.close()` in `finally` blocks
3. Wrong time periods → Check `get_time_period()` hour boundaries

## Key Files

- `database/schema.sql` - Full PostgreSQL DDL
- `routes/billing.py` - Most mature module, copy patterns from here
- `services/database.py` - 1225 lines of SQL queries (god class, needs refactoring)
- `DOCS/PLAN.md` - Project roadmap and phase tracking

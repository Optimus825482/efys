"""Quick database table check"""
import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect('postgresql://postgres:518518Erkan@localhost:5432/osos_db')
cur = conn.cursor(cursor_factory=RealDictCursor)

tables = ['subscribers', 'meters', 'readings', 'tariffs', 'invoices', 'billing_periods', 
          'payments', 'alarms', 'users', 'system_logs', 'scheduled_readings', 
          'additional_charges', 'subscriber_daily_averages']

print('=== DATABASE TABLE STATUS ===')
for table in tables:
    try:
        cur.execute(f'SELECT COUNT(*) as count FROM {table}')
        result = cur.fetchone()
        count = result['count']
        status = '✓' if count > 0 else '✗ EMPTY'
        print(f'{status} {table}: {count} rows')
    except Exception as e:
        print(f'✗ {table}: ERROR - {e}')

conn.close()

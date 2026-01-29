"""Check all tariff tables schema"""
from services.database import DatabaseService

db = DatabaseService()
try:
    tables = ['tariffs', 'osb_distribution_tariffs', 'edas_tariffs', 'osb_billing_settings']
    
    for table in tables:
        db.cur.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table}' 
            ORDER BY ordinal_position
        """)
        print(f"\n=== {table.upper()} ===")
        for row in db.cur.fetchall():
            print(f"  {row['column_name']}: {row['data_type']}")
finally:
    db.close()

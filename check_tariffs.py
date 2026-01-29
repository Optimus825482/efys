"""Tarife yapısı analizi"""
from services.database import DatabaseService

db = DatabaseService()

# Mevcut tarifeler
db.cur.execute('SELECT id, name, tariff_type, t1_rate, t2_rate, t3_rate, reactive_rate, distribution_fee, is_active FROM tariffs')
tariffs = db.cur.fetchall()
print('=== ENERJİ TARİFELERİ ===')
for t in tariffs:
    print(f"  {t['id']}: {t['name']} | T1:{t['t1_rate']} T2:{t['t2_rate']} T3:{t['t3_rate']} | Aktif:{t['is_active']}")

# OSB Dağıtım Tarifeleri
print('\n=== OSB DAĞITIM TARİFELERİ ===')
try:
    db.cur.execute('SELECT * FROM osb_distribution_tariffs LIMIT 3')
    osb = db.cur.fetchall()
    for o in osb:
        print(f"  {dict(o)}")
except Exception as e:
    print(f"  Tablo yok veya boş: {e}")

# EDAŞ Tarifeleri
print('\n=== EDAŞ TAVAN TARİFELERİ ===')
try:
    db.cur.execute('SELECT * FROM edas_tariffs LIMIT 2')
    edas = db.cur.fetchall()
    for e in edas:
        print(f"  {dict(e)}")
except Exception as e:
    print(f"  Tablo yok veya boş: {e}")

# OSB Billing Settings
print('\n=== OSB FATURALAMA AYARLARI ===')
try:
    db.cur.execute('SELECT setting_key, setting_value, description FROM osb_billing_settings')
    settings = db.cur.fetchall()
    for s in settings:
        print(f"  {s['setting_key']}: {s['setting_value']} ({s['description']})")
except Exception as e:
    print(f"  Tablo yok veya boş: {e}")

db.close()

"""
EFYS Demo Veri Tamamlayıcı
Boş tabloları gerçekçi demo verilerle doldurur:
- invoices (faturalar)
- payments (ödemeler)
- alarms (alarmlar)
- system_logs (sistem logları)
- scheduled_readings (zamanlanmış okumalar)
"""

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from datetime import datetime, timedelta
from decimal import Decimal
import random

DB_URL = "postgresql://postgres:518518Erkan@localhost:5432/osos_db"

def get_connection():
    return psycopg2.connect(DB_URL)

def generate_invoices():
    """Ocak 2026 için tüm abonelere fatura oluştur"""
    print("📄 Faturalar oluşturuluyor...")
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Billing period al
    cur.execute("SELECT id FROM billing_periods LIMIT 1")
    period = cur.fetchone()
    if not period:
        # Billing period oluştur
        cur.execute("""
            INSERT INTO billing_periods (name, period_start, period_end, invoice_date, due_date, status)
            VALUES ('2026 Ocak', '2026-01-01', '2026-01-31', '2026-02-01', '2026-02-15', 'open')
            RETURNING id
        """)
        period_id = cur.fetchone()['id']
    else:
        period_id = period['id']
    
    # Tüm aboneleri al
    cur.execute("""
        SELECT 
            s.id as subscriber_id,
            s.subscriber_code,
            s.name,
            s.tariff_id,
            m.id as meter_id,
            t.t1_rate, t.t2_rate, t.t3_rate, t.reactive_rate
        FROM subscribers s
        JOIN meters m ON s.id = m.subscriber_id
        JOIN tariffs t ON s.tariff_id = t.id
        WHERE s.status = 'Aktif'
    """)
    subscribers = cur.fetchall()
    
    invoices = []
    invoice_no = 1
    
    for sub in subscribers:
        # Bu abone için tüketim hesapla
        cur.execute("""
            SELECT 
                COALESCE(SUM(t1_consumption), 0) as t1,
                COALESCE(SUM(t2_consumption), 0) as t2,
                COALESCE(SUM(t3_consumption), 0) as t3,
                COALESCE(SUM(total_consumption), 0) as total,
                COALESCE(SUM(inductive_reactive), 0) as inductive,
                COALESCE(SUM(capacitive_reactive), 0) as capacitive
            FROM readings
            WHERE meter_id = %s
            AND reading_time >= '2026-01-01' AND reading_time < '2026-02-01'
        """, (sub['meter_id'],))
        consumption = cur.fetchone()
        
        # Tutarları hesapla
        t1_amount = float(consumption['t1']) * float(sub['t1_rate'])
        t2_amount = float(consumption['t2']) * float(sub['t2_rate'])
        t3_amount = float(consumption['t3']) * float(sub['t3_rate'])
        
        # Reaktif ceza
        total_reactive = float(consumption['inductive']) + float(consumption['capacitive'])
        total_active = float(consumption['total'])
        reactive_amount = 0
        if total_active > 0:
            tan_phi = total_reactive / total_active
            if tan_phi > 0.484:  # cos phi < 0.9
                excess = total_reactive - (total_active * 0.484)
                reactive_amount = excess * float(sub['reactive_rate'])
        
        subtotal = t1_amount + t2_amount + t3_amount + reactive_amount
        vat_amount = subtotal * 0.20
        total_amount = subtotal + vat_amount
        
        # Status belirle (bazıları ödendi, bazıları bekliyor)
        status_options = ['paid', 'paid', 'paid', 'issued', 'issued', 'draft']
        status = random.choice(status_options)
        
        invoice_data = (
            f"FTR-2026-{invoice_no:05d}",  # invoice_no
            sub['subscriber_id'],
            sub['meter_id'],
            period_id,
            sub['tariff_id'],
            round(consumption['t1'], 3),
            round(consumption['t2'], 3),
            round(consumption['t3'], 3),
            round(consumption['total'], 3),
            round(consumption['inductive'], 3),
            round(consumption['capacitive'], 3),
            round(t1_amount, 2),
            round(t2_amount, 2),
            round(t3_amount, 2),
            round(reactive_amount, 2),
            0,  # distribution_amount
            round(subtotal, 2),
            20.00,  # vat_rate
            round(vat_amount, 2),
            round(total_amount, 2),
            status,
            datetime(2026, 2, 1),  # issue_date
            datetime(2026, 2, 15),  # due_date
            datetime(2026, 2, 10) if status == 'paid' else None  # paid_at
        )
        invoices.append(invoice_data)
        invoice_no += 1
    
    # Toplu insert
    execute_values(cur, """
        INSERT INTO invoices (
            invoice_no, subscriber_id, meter_id, period_id, tariff_id,
            t1_consumption, t2_consumption, t3_consumption, total_consumption,
            inductive_reactive, capacitive_reactive,
            t1_amount, t2_amount, t3_amount, reactive_amount, distribution_amount,
            subtotal, vat_rate, vat_amount, total_amount,
            status, issue_date, due_date, paid_at
        ) VALUES %s
    """, invoices)
    
    conn.commit()
    print(f"  ✓ {len(invoices)} fatura oluşturuldu")
    
    cur.close()
    conn.close()
    return len(invoices)

def generate_alarms():
    """Sistem alarmları oluştur"""
    print("🚨 Alarmlar oluşturuluyor...")
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    alarm_templates = [
        ('METER', 'warning', 'Sayaç bağlantısı zayıf - sinyal gücü düşük'),
        ('METER', 'info', 'Sayaç firmware güncellemesi mevcut'),
        ('POWER', 'critical', 'Güç faktörü kritik seviyede (< 0.85)'),
        ('POWER', 'warning', 'Reaktif enerji limiti aşıldı'),
        ('CONSUMPTION', 'info', 'Tüketim %20 üzerinde artış tespit edildi'),
        ('CONSUMPTION', 'warning', 'Anormal tüketim paterni tespit edildi'),
        ('SYSTEM', 'info', 'Günlük okuma tamamlandı'),
        ('SYSTEM', 'warning', 'Bazı sayaçlardan veri alınamadı'),
        ('BILLING', 'info', 'Fatura dönemi açıldı'),
        ('BILLING', 'warning', 'Vadesi geçmiş fatura tespit edildi'),
    ]
    
    alarms = []
    now = datetime.now()
    
    for i in range(30):
        template = random.choice(alarm_templates)
        created_at = now - timedelta(hours=random.randint(1, 168))  # Son 1 hafta
        acknowledged = random.choice([True, True, False])
        
        alarm_data = (
            template[0],  # source
            template[1],  # severity
            template[2],  # message
            acknowledged,
            created_at if acknowledged else None,  # acknowledged_at
            created_at + timedelta(hours=1) if acknowledged else None,  # resolved_at
            created_at
        )
        alarms.append(alarm_data)
    
    execute_values(cur, """
        INSERT INTO alarms (source, severity, message, acknowledged, acknowledged_at, resolved_at, created_at)
        VALUES %s
    """, alarms)
    
    conn.commit()
    print(f"  ✓ {len(alarms)} alarm kaydı oluşturuldu")
    
    cur.close()
    conn.close()
    return len(alarms)

def generate_system_logs():
    """Sistem logları oluştur"""
    print("📝 Sistem logları oluşturuluyor...")
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    log_templates = [
        ('INFO', 'Okuma', 'Günlük okuma işlemi başlatıldı'),
        ('INFO', 'Okuma', 'Toplu okuma tamamlandı - 30/30 başarılı'),
        ('INFO', 'Fatura', 'Fatura hesaplama işlemi tamamlandı'),
        ('INFO', 'Sistem', 'Sistem başlatıldı'),
        ('INFO', 'Sistem', 'Veritabanı yedekleme tamamlandı'),
        ('WARN', 'Okuma', 'Bazı sayaçlara bağlanılamadı - yeniden deneniyor'),
        ('WARN', 'Sistem', 'Disk kullanımı %80 üzerinde'),
        ('WARN', 'Fatura', 'Vadesi geçmiş faturalar tespit edildi'),
        ('ERROR', 'Okuma', 'Sayaç M-000015 bağlantı hatası'),
        ('ERROR', 'Sistem', 'E-posta sunucusuna bağlanılamadı'),
    ]
    
    logs = []
    now = datetime.now()
    
    for i in range(50):
        template = random.choice(log_templates)
        created_at = now - timedelta(hours=random.randint(1, 720))  # Son 30 gün
        
        log_data = (
            template[0],  # log_level
            template[1],  # module
            template[2],  # message
            1,  # user_id (admin)
            created_at
        )
        logs.append(log_data)
    
    execute_values(cur, """
        INSERT INTO system_logs (log_level, module, message, user_id, created_at)
        VALUES %s
    """, logs)
    
    conn.commit()
    print(f"  ✓ {len(logs)} log kaydı oluşturuldu")
    
    cur.close()
    conn.close()
    return len(logs)

def generate_scheduled_readings():
    """Zamanlanmış okumalar oluştur"""
    print("⏰ Zamanlanmış okumalar oluşturuluyor...")
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Sayaçları al
    cur.execute("SELECT id FROM meters")
    meters = [m['id'] for m in cur.fetchall()]
    
    readings = []
    now = datetime.now()
    
    # Geçmiş okumalar (tamamlanmış)
    for i in range(20):
        meter_id = random.choice(meters)
        scheduled_time = now - timedelta(hours=random.randint(1, 168))
        executed_at = scheduled_time + timedelta(minutes=random.randint(0, 5))
        
        reading_data = (
            meter_id,
            scheduled_time,
            executed_at,
            'completed'
        )
        readings.append(reading_data)
    
    # Gelecek okumalar (bekleyen)
    for i in range(10):
        meter_id = random.choice(meters)
        scheduled_time = now + timedelta(hours=random.randint(1, 48))
        
        reading_data = (
            meter_id,
            scheduled_time,
            None,
            'pending'
        )
        readings.append(reading_data)
    
    execute_values(cur, """
        INSERT INTO scheduled_readings (meter_id, scheduled_time, executed_at, status)
        VALUES %s
    """, readings)
    
    conn.commit()
    print(f"  ✓ {len(readings)} zamanlanmış okuma oluşturuldu")
    
    cur.close()
    conn.close()
    return len(readings)

def main():
    print("\n" + "="*60)
    print("EFYS Demo Veri Tamamlayıcı")
    print("="*60 + "\n")
    
    # Tek connection kullan
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    print("🗑️  Mevcut demo veriler temizleniyor...")
    cur.execute("DELETE FROM additional_charges")
    cur.execute("DELETE FROM invoices")
    cur.execute("DELETE FROM alarms WHERE source IS NOT NULL")
    cur.execute("DELETE FROM system_logs")
    cur.execute("DELETE FROM scheduled_readings")
    conn.commit()
    print("  ✓ Temizlik tamamlandı\n")
    
    # Yeni veriler oluştur (aynı connection ile)
    invoice_count = generate_invoices_with_conn(conn, cur)
    alarm_count = generate_alarms_with_conn(conn, cur)
    log_count = generate_system_logs_with_conn(conn, cur)
    scheduled_count = generate_scheduled_readings_with_conn(conn, cur)
    
    cur.close()
    conn.close()
    
    print("\n" + "="*60)
    print("ÖZET")
    print("="*60)
    print(f"  Faturalar:              {invoice_count}")
    print(f"  Alarmlar:               {alarm_count}")
    print(f"  Sistem Logları:         {log_count}")
    print(f"  Zamanlanmış Okumalar:   {scheduled_count}")
    print("="*60)
    print("✅ Demo veriler başarıyla oluşturuldu!")
    print()

if __name__ == "__main__":
    main()

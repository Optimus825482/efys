"""
EFYS Database Service Extensions
Eksik fonksiyonların implementasyonları
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from datetime import datetime, timedelta
from decimal import Decimal
import os

# Database URL
DATABASE_URL = (
    os.environ.get("DATABASE_URL")
    or "postgresql://postgres:518518Erkan@localhost:5432/osos_db"
)


@contextmanager
def get_db():
    """Database connection context manager"""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_cursor(conn):
    """Get a cursor that returns dicts"""
    return conn.cursor(cursor_factory=RealDictCursor)


# =============================================================================
# OKUMA İŞLEMLERİ - EKSİK FONKSİYONLAR
# =============================================================================


def get_scheduled_jobs():
    """Zamanlanmış okuma görevleri (Demo)"""
    # Demo veri - gerçek sistemde cron job tablosundan gelecek
    return [
        {
            "id": 1,
            "name": "Günlük Okuma - 00:00",
            "schedule": "0 0 * * *",
            "status": "active",
            "last_run": datetime.now() - timedelta(hours=1),
            "next_run": datetime.now() + timedelta(hours=23),
            "success_count": 28,
            "fail_count": 2,
        },
        {
            "id": 2,
            "name": "Saatlik Okuma - Her Saat Başı",
            "schedule": "0 * * * *",
            "status": "active",
            "last_run": datetime.now() - timedelta(minutes=15),
            "next_run": datetime.now() + timedelta(minutes=45),
            "success_count": 672,
            "fail_count": 8,
        },
        {
            "id": 3,
            "name": "Haftalık Rapor - Pazartesi 08:00",
            "schedule": "0 8 * * 1",
            "status": "active",
            "last_run": datetime.now() - timedelta(days=6),
            "next_run": datetime.now() + timedelta(days=1),
            "success_count": 4,
            "fail_count": 0,
        },
    ]


def get_failed_readings(limit=50):
    """Başarısız okumalar"""
    with get_db() as conn:
        cur = get_cursor(conn)

        cur.execute(
            """
            SELECT 
                r.id,
                r.reading_time,
                m.meter_no,
                s.name as subscriber_name,
                r.reading_status as error_reason,
                r.created_at
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            JOIN subscribers s ON m.subscriber_id = s.id
            WHERE r.reading_status IN ('failed', 'pending', 'error')
            ORDER BY r.reading_time DESC
            LIMIT %s
        """,
            (limit,),
        )

        return [dict(row) for row in cur.fetchall()]


def retry_failed_reading(reading_id):
    """Başarısız okumayı tekrar dene (Demo)"""
    with get_db() as conn:
        cur = get_cursor(conn)

        # Demo: Status'u pending yap
        cur.execute(
            """
            UPDATE readings
            SET reading_status = 'pending'
            WHERE id = %s
            RETURNING id
        """,
            (reading_id,),
        )

        result = cur.fetchone()
        return (
            {"success": True, "reading_id": result["id"]}
            if result
            else {"success": False}
        )


def start_bulk_reading(meter_ids):
    """Toplu okuma başlat (Demo)"""
    # Demo: Başarı mesajı döndür
    return {
        "success": True,
        "message": f"{len(meter_ids)} sayaç için okuma başlatıldı",
        "meter_count": len(meter_ids),
        "estimated_duration": len(meter_ids) * 2,  # saniye
    }


# =============================================================================
# FATURALAMA - EKSİK FONKSİYONLAR
# =============================================================================


def create_invoice(subscriber_id, period_id, tariff_id):
    """
    Fatura oluştur ve kaydet - EPDK OSB Faturalama Modeli
    
    Kalemler:
    1. Aktif Enerji (T1/T2/T3 zamanlı)
    2. Dağıtım Bedeli (OG/AG + EDAŞ tavan kontrolü)
    3. Teknik Kayıp Payı
    4. İletim Bedeli (TEİAŞ)
    5. Reaktif Ceza (Endüktif %20, Kapasitif %15)
    6. Güç Bedeli (çift terimli)
    7. GES Mahsuplaşma
    8. BTV + KDV
    """
    from services.osb_billing import OSBBillingService
    
    service = OSBBillingService()
    try:
        # EPDK uyumlu OSB fatura hesaplamasını kullan
        invoice_data = service.calculate_osb_invoice(subscriber_id, period_id)
        if not invoice_data:
            return {"success": False, "error": "Fatura hesaplanamadı"}
        
        with get_db() as conn:
            cur = get_cursor(conn)
            
            # Fatura numarası oluştur
            cur.execute(
                "SELECT COUNT(*) as count FROM invoices WHERE period_id = %s", (period_id,)
            )
            count = cur.fetchone()["count"]
            period_name = invoice_data['period']['name'].replace(' ', '')
            invoice_no = f"FTR-{period_name}-{count + 1:05d}"

            # Faturayı kaydet (OSB modeli ile)
            cur.execute(
                """
                INSERT INTO invoices (
                    invoice_no, subscriber_id, meter_id, period_id, tariff_id,
                    t1_consumption, t2_consumption, t3_consumption, total_consumption,
                    inductive_reactive, capacitive_reactive,
                    t1_amount, t2_amount, t3_amount, reactive_amount,
                    distribution_amount, technical_loss_share, technical_loss_amount, 
                    transmission_amount, btv_amount,
                    subtotal, vat_rate, vat_amount, total_amount,
                    status, issue_date, due_date
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    'issued', %s, %s
                ) RETURNING id
            """,
                (
                    invoice_no,
                    subscriber_id,
                    invoice_data['meter_id'],
                    period_id,
                    tariff_id,
                    invoice_data['consumption']['t1'],
                    invoice_data['consumption']['t2'],
                    invoice_data['consumption']['t3'],
                    invoice_data['consumption']['total'],
                    invoice_data['consumption']['inductive'],
                    invoice_data['consumption']['capacitive'],
                    invoice_data['t1_amount'],
                    invoice_data['t2_amount'],
                    invoice_data['t3_amount'],
                    invoice_data['reactive_amount'],
                    invoice_data['distribution_amount'],
                    invoice_data['technical_loss_share'],
                    invoice_data['technical_loss_amount'],
                    invoice_data['transmission_amount'],
                    invoice_data['btv_amount'],
                    invoice_data['subtotal'],
                    invoice_data['kdv_rate'] * 100,
                    invoice_data['kdv_amount'],
                    invoice_data['total_amount'],
                    invoice_data['period']['invoice_date'],
                    invoice_data['period']['due_date'],
                ),
            )

            invoice_id = cur.fetchone()["id"]
            
            # Fatura kalemlerini oluştur (EPDK modeli)
            items_data = [
                ('energy', 'T1 - Gündüz Tüketimi (06:00-17:00)', invoice_data['consumption']['t1'], 
                 invoice_data['t1_rate'], invoice_data['t1_amount']),
                ('energy', 'T2 - Puant Tüketimi (17:00-22:00)', invoice_data['consumption']['t2'], 
                 invoice_data['t2_rate'], invoice_data['t2_amount']),
                ('energy', 'T3 - Gece Tüketimi (22:00-06:00)', invoice_data['consumption']['t3'], 
                 invoice_data['t3_rate'], invoice_data['t3_amount']),
                ('distribution', f"OSB Dağıtım Bedeli ({invoice_data.get('voltage_level', 'OG')})", 
                 invoice_data.get('net_consumption', invoice_data['consumption']['total']), 
                 invoice_data['distribution_rate'], invoice_data['distribution_amount']),
                ('technical_loss', 'Teknik Kayıp Payı', invoice_data['technical_loss_share'], 
                 0, invoice_data['technical_loss_amount']),
                ('transmission', 'TEİAŞ İletim Bedeli', invoice_data.get('net_consumption', invoice_data['consumption']['total']), 
                 invoice_data['transmission_rate'], invoice_data['transmission_amount']),
            ]
            
            # Reaktif ceza
            if invoice_data['reactive_amount'] > 0:
                reactive_label = 'Reaktif Enerji Cezası (Endüktif > %20)' if invoice_data.get('reactive_type') == 'inductive' else 'Reaktif Enerji Cezası (Kapasitif > %15)'
                items_data.append(
                    ('reactive', reactive_label, 
                     invoice_data['consumption']['inductive'] + invoice_data['consumption']['capacitive'],
                     invoice_data['reactive_rate'], invoice_data['reactive_amount'])
                )
            
            # Güç bedeli (çift terimli)
            if invoice_data.get('capacity_amount', 0) > 0:
                items_data.append(
                    ('capacity', 'Güç Bedeli (Sözleşme Gücü)', 
                     invoice_data['subscriber'].get('contract_demand', 0),
                     0, invoice_data['capacity_amount'])
                )
            
            # Güç aşım bedeli
            if invoice_data.get('capacity_excess_amount', 0) > 0:
                items_data.append(
                    ('capacity_excess', 'Güç Aşım Bedeli', 
                     invoice_data['consumption'].get('max_demand', 0),
                     0, invoice_data['capacity_excess_amount'])
                )
            
            # GES kredi
            if invoice_data.get('solar_credit_amount', 0) > 0:
                items_data.append(
                    ('solar_credit', 'GES Üretim Kredisi', 
                     invoice_data['solar']['exported'],
                     0, -invoice_data['solar_credit_amount'])  # Negatif değer (indirim)
                )
            
            for item_type, desc, qty, price, amount in items_data:
                if amount and float(amount) > 0:
                    cur.execute(
                        """
                        INSERT INTO invoice_items (invoice_id, item_type, description, quantity, unit_price, total_amount)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                        (invoice_id, item_type, desc, qty, price, amount),
                    )

            return {
                "success": True,
                "invoice_id": invoice_id,
                "invoice_no": invoice_no,
                "total_amount": invoice_data['total_amount'],
            }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        service.close()


def bulk_create_invoices(period_id):
    """Toplu fatura oluşturma"""
    with get_db() as conn:
        cur = get_cursor(conn)

        # Aktif aboneleri al
        cur.execute("""
            SELECT id, tariff_id 
            FROM subscribers 
            WHERE status = 'Aktif'
        """)
        subscribers = cur.fetchall()

        success_count = 0
        fail_count = 0
        results = []

        for sub in subscribers:
            result = create_invoice(sub["id"], period_id, sub["tariff_id"])
            if result["success"]:
                success_count += 1
                results.append(
                    {
                        "subscriber_id": sub["id"],
                        "invoice_no": result["invoice_no"],
                        "amount": result["total_amount"],
                    }
                )
            else:
                fail_count += 1

        return {
            "success": True,
            "total": len(subscribers),
            "success_count": success_count,
            "fail_count": fail_count,
            "invoices": results,
        }


def get_invoice_preview(subscriber_id, period_id):
    """
    Fatura önizleme (kaydetmeden hesapla) - EPDK OSB Faturalama Modeli
    
    Kalemler:
    1. Aktif Enerji (T1/T2/T3 zamanlı)
    2. Dağıtım Bedeli (OG/AG + EDAŞ tavan kontrolü)
    3. Teknik Kayıp Payı
    4. İletim Bedeli (TEİAŞ)
    5. Reaktif Ceza (Endüktif %20, Kapasitif %15)
    6. Güç Bedeli (çift terimli)
    7. GES Mahsuplaşma
    8. BTV + KDV
    """
    from services.osb_billing import OSBBillingService
    
    service = OSBBillingService()
    try:
        # EPDK uyumlu OSB fatura hesaplamasını kullan
        invoice = service.calculate_osb_invoice(subscriber_id, period_id)
        if not invoice:
            return None
        
        return invoice
    finally:
        service.close()


def cancel_invoice(invoice_id, reason):
    """Fatura iptali"""
    with get_db() as conn:
        cur = get_cursor(conn)

        cur.execute(
            """
            UPDATE invoices
            SET status = 'cancelled',
                cancelled_at = CURRENT_TIMESTAMP,
                cancel_reason = %s
            WHERE id = %s
            RETURNING invoice_no
        """,
            (reason, invoice_id),
        )

        result = cur.fetchone()
        return (
            {"success": True, "invoice_no": result["invoice_no"]}
            if result
            else {"success": False}
        )


def add_additional_charge(invoice_id, charge_type, amount, description):
    """Ek kalem ekleme"""
    with get_db() as conn:
        cur = get_cursor(conn)

        # Fatura bilgilerini al
        cur.execute("SELECT subscriber_id FROM invoices WHERE id = %s", (invoice_id,))
        invoice = cur.fetchone()

        if not invoice:
            return {"success": False, "error": "Fatura bulunamadı"}

        # Ek kalemi ekle
        cur.execute(
            """
            INSERT INTO additional_charges (invoice_id, subscriber_id, charge_type, amount, description)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """,
            (invoice_id, invoice["subscriber_id"], charge_type, amount, description),
        )

        charge_id = cur.fetchone()["id"]

        # Fatura toplamını güncelle
        cur.execute(
            """
            UPDATE invoices
            SET total_amount = total_amount + %s
            WHERE id = %s
        """,
            (amount, invoice_id),
        )

        return {"success": True, "charge_id": charge_id}


# =============================================================================
# ABONE İŞLEMLERİ - EKSİK FONKSİYONLAR
# =============================================================================


def create_subscriber(data):
    """Yeni abone oluştur"""
    with get_db() as conn:
        cur = get_cursor(conn)

        # Abone kodu oluştur
        cur.execute("SELECT COUNT(*) as count FROM subscribers")
        count = cur.fetchone()["count"]
        subscriber_code = f"A-{count + 1:06d}"

        cur.execute(
            """
            INSERT INTO subscribers (
                subscriber_code, name, tax_no, tax_office, address, phone, email,
                ada, parsel, area_m2, sector, subscriber_type, tariff_id,
                contract_demand, status
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Aktif'
            ) RETURNING id
        """,
            (
                subscriber_code,
                data["name"],
                data.get("tax_no"),
                data.get("tax_office"),
                data.get("address"),
                data.get("phone"),
                data.get("email"),
                data.get("ada"),
                data.get("parsel"),
                data.get("area_m2"),
                data.get("sector", "Diğer"),
                data.get("subscriber_type", "Sanayi"),
                data.get("tariff_id"),
                data.get("contract_demand"),
            ),
        )

        subscriber_id = cur.fetchone()["id"]
        return {
            "success": True,
            "subscriber_id": subscriber_id,
            "subscriber_code": subscriber_code,
        }


def update_subscriber(subscriber_id, data):
    """Abone güncelle"""
    with get_db() as conn:
        cur = get_cursor(conn)

        # Dinamik UPDATE query oluştur
        fields = []
        values = []
        for key, value in data.items():
            if key != "id":
                fields.append(f"{key} = %s")
                values.append(value)

        values.append(subscriber_id)

        cur.execute(
            f"""
            UPDATE subscribers
            SET {", ".join(fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id
        """,
            values,
        )

        result = cur.fetchone()
        return {"success": True} if result else {"success": False}


def delete_subscriber(subscriber_id):
    """Abone silme (soft delete)"""
    with get_db() as conn:
        cur = get_cursor(conn)

        cur.execute(
            """
            UPDATE subscribers
            SET status = 'Kapalı', updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id
        """,
            (subscriber_id,),
        )

        result = cur.fetchone()
        return {"success": True} if result else {"success": False}


def assign_meter_to_subscriber(meter_id, subscriber_id):
    """Sayaç atama"""
    with get_db() as conn:
        cur = get_cursor(conn)

        cur.execute(
            """
            UPDATE meters
            SET subscriber_id = %s
            WHERE id = %s
            RETURNING meter_no
        """,
            (subscriber_id, meter_id),
        )

        result = cur.fetchone()
        return (
            {"success": True, "meter_no": result["meter_no"]}
            if result
            else {"success": False}
        )


# =============================================================================
# ALARM SİSTEMİ - EKSİK FONKSİYONLAR
# =============================================================================


def get_alarms(limit=50, severity=None):
    """Alarm listesi (Demo - gerçek sistemde alarms tablosundan gelecek)"""
    alarms = [
        {
            "id": 1,
            "type": "reactive_penalty",
            "severity": "critical",
            "message": "Gönen Yem Fabrikası - Reaktif enerji %22 (Ceza riski)",
            "subscriber_id": 1,
            "created_at": datetime.now() - timedelta(minutes=5),
            "status": "active",
        },
        {
            "id": 2,
            "type": "demand_exceeded",
            "severity": "warning",
            "message": "Bandırma Çelik - Sözleşme gücü %95 kullanımda",
            "subscriber_id": 2,
            "created_at": datetime.now() - timedelta(minutes=15),
            "status": "active",
        },
        {
            "id": 3,
            "type": "reading_failed",
            "severity": "warning",
            "message": "ELK-015 sayacı 3 saattir okunamıyor",
            "subscriber_id": 15,
            "created_at": datetime.now() - timedelta(hours=3),
            "status": "active",
        },
        {
            "id": 4,
            "type": "payment_overdue",
            "severity": "info",
            "message": "5 abonenin faturası vadesi geçti",
            "subscriber_id": None,
            "created_at": datetime.now() - timedelta(days=1),
            "status": "active",
        },
    ]

    if severity:
        alarms = [a for a in alarms if a["severity"] == severity]

    return alarms[:limit]


def get_alarm_stats():
    """Alarm istatistikleri"""
    alarms = get_alarms(limit=1000)
    return {
        "total": len(alarms),
        "critical": len([a for a in alarms if a["severity"] == "critical"]),
        "warning": len([a for a in alarms if a["severity"] == "warning"]),
        "info": len([a for a in alarms if a["severity"] == "info"]),
        "active": len([a for a in alarms if a["status"] == "active"]),
    }


# =============================================================================
# VEE VE EKSİK VERİ - EKSİK FONKSİYONLAR
# =============================================================================


def get_missing_data_stats(start_date=None, end_date=None):
    """Eksik veri istatistikleri"""
    if start_date is None:
        start_date = datetime.now().date() - timedelta(days=7)
    if end_date is None:
        end_date = datetime.now().date()

    with get_db() as conn:
        cur = get_cursor(conn)

        # Beklenen okuma sayısı (her online sayaç için 96 okuma/gün - 15 dakikalık)
        cur.execute(
            "SELECT COUNT(*) as meter_count FROM meters WHERE status = 'online'"
        )
        meter_count = cur.fetchone()["meter_count"]

        days = (end_date - start_date).days + 1
        expected_readings = meter_count * 96 * days

        # Gerçekleşen okuma sayısı (online sayaçlar)
        cur.execute(
            """
            SELECT COUNT(*) as actual_readings
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            WHERE m.status = 'online'
            AND r.reading_time BETWEEN %s AND %s
        """,
            (start_date, end_date),
        )
        actual_readings = cur.fetchone()["actual_readings"]

        missing_count = max(expected_readings - actual_readings, 0)
        completion_rate = (
            round(actual_readings / expected_readings * 100, 2)
            if expected_readings > 0
            else 0
        )
        completion_rate = min(completion_rate, 100)

        return {
            "expected": expected_readings,
            "actual": actual_readings,
            "missing": missing_count,
            "completion_rate": completion_rate,
        }


def get_missing_data(limit=50):
    """Eksik veri listesi"""
    with get_db() as conn:
        cur = get_cursor(conn)

        cur.execute(
            """
            SELECT
                m.id as meter_id,
                m.meter_no as meter_serial,
                s.name as subscriber_name,
                MAX(r.reading_time) as last_reading
            FROM meters m
            JOIN subscribers s ON m.subscriber_id = s.id
            LEFT JOIN readings r ON r.meter_id = m.id
            GROUP BY m.id, m.meter_no, s.name
            HAVING MAX(r.reading_time) IS NULL
               OR MAX(r.reading_time) < NOW() - INTERVAL '1 hour'
            ORDER BY last_reading NULLS FIRST
            LIMIT %s
        """,
            (limit,),
        )

        rows = [dict(row) for row in cur.fetchall()]

    results = []
    now = datetime.now()
    for idx, row in enumerate(rows, start=1):
        last_reading = row.get("last_reading") or (now - timedelta(hours=1))
        duration_minutes = int((now - last_reading).total_seconds() / 60)
        if duration_minutes >= 360:
            priority = "high"
        elif duration_minutes >= 120:
            priority = "medium"
        else:
            priority = "low"

        results.append(
            {
                "id": idx,
                "meter_id": row.get("meter_id"),
                "meter_serial": row.get("meter_serial"),
                "subscriber_name": row.get("subscriber_name"),
                "missing_date": last_reading.date().isoformat(),
                "missing_hour": last_reading.strftime("%H:%M"),
                "data_type": "total_consumption",
                "expected_value": None,
                "estimated_value": None,
                "status": "pending",
                "priority": priority,
            }
        )

    return results


def estimate_missing_data(meter_id, missing_time):
    """Eksik veri tahmini (geçmiş ortalama)"""
    with get_db() as conn:
        cur = get_cursor(conn)

        # Aynı saat dilimindeki geçmiş 7 günün ortalaması
        hour = missing_time.hour
        cur.execute(
            """
            SELECT 
                AVG(total_consumption) as avg_consumption,
                AVG(power_factor) as avg_pf
            FROM readings
            WHERE meter_id = %s
            AND EXTRACT(hour FROM reading_time) = %s
            AND reading_time >= %s - INTERVAL '7 days'
            AND reading_time < %s
        """,
            (meter_id, hour, missing_time, missing_time),
        )

        result = cur.fetchone()

        return {
            "estimated_consumption": float(result["avg_consumption"] or 0),
            "estimated_pf": float(result["avg_pf"] or 0.9),
            "method": "historical_average",
        }


# =============================================================================
# RAPORLAMA - EKSİK FONKSİYONLAR
# =============================================================================


def get_index_report(start_date, end_date):
    """Endeks raporu"""
    with get_db() as conn:
        cur = get_cursor(conn)

        cur.execute(
            """
            WITH first_readings AS (
                SELECT DISTINCT ON (meter_id)
                    meter_id,
                    t1_index as first_t1,
                    t2_index as first_t2,
                    t3_index as first_t3,
                    reading_time as first_time
                FROM readings
                WHERE reading_time >= %s
                ORDER BY meter_id, reading_time ASC
            ),
            last_readings AS (
                SELECT DISTINCT ON (meter_id)
                    meter_id,
                    t1_index as last_t1,
                    t2_index as last_t2,
                    t3_index as last_t3,
                    reading_time as last_time
                FROM readings
                WHERE reading_time <= %s
                ORDER BY meter_id, reading_time DESC
            )
            SELECT 
                m.meter_no,
                s.name as subscriber_name,
                f.first_t1, f.first_t2, f.first_t3,
                l.last_t1, l.last_t2, l.last_t3,
                (l.last_t1 - f.first_t1) as diff_t1,
                (l.last_t2 - f.first_t2) as diff_t2,
                (l.last_t3 - f.first_t3) as diff_t3,
                f.first_time,
                l.last_time
            FROM meters m
            JOIN subscribers s ON m.subscriber_id = s.id
            LEFT JOIN first_readings f ON m.id = f.meter_id
            LEFT JOIN last_readings l ON m.id = l.meter_id
            ORDER BY m.meter_no
        """,
            (start_date, end_date),
        )

        return [dict(row) for row in cur.fetchall()]


# =============================================================================
# ADDITIONAL FUNCTIONS FOR ROUTES
# =============================================================================


def preview_invoice(subscriber_id, period_id):
    """Fatura önizleme - get_invoice_preview'in alias'ı"""
    return get_invoice_preview(subscriber_id, period_id)


def add_additional_item(invoice_id, description, amount):
    """Ek kalem ekleme - add_additional_charge'ın wrapper'ı"""
    return add_additional_charge(invoice_id, "additional", amount, description)


def get_invoice_by_id(invoice_id):
    """Fatura detayı"""
    with get_db() as conn:
        cur = get_cursor(conn)

        cur.execute(
            """
            SELECT 
                i.*,
                s.subscriber_code,
                s.name as subscriber_name,
                s.address,
                bp.period_name,
                bp.period_start,
                bp.period_end
            FROM invoices i
            JOIN subscribers s ON i.subscriber_id = s.id
            JOIN billing_periods bp ON i.period_id = bp.id
            WHERE i.id = %s
        """,
            (invoice_id,),
        )

        invoice = cur.fetchone()
        if not invoice:
            return None

        # Fatura kalemlerini al
        cur.execute(
            """
            SELECT * FROM invoice_items
            WHERE invoice_id = %s
            ORDER BY id
        """,
            (invoice_id,),
        )

        items = [dict(row) for row in cur.fetchall()]

        result = dict(invoice)
        result["items"] = items
        return result


def get_invoices_by_period(period_id):
    """Döneme göre faturalar"""
    with get_db() as conn:
        cur = get_cursor(conn)

        cur.execute(
            """
            SELECT 
                i.*,
                s.subscriber_code,
                s.name as subscriber_name
            FROM invoices i
            JOIN subscribers s ON i.subscriber_id = s.id
            WHERE i.period_id = %s
            ORDER BY i.invoice_date DESC
        """,
            (period_id,),
        )

        return [dict(row) for row in cur.fetchall()]


def get_unpaid_invoices():
    """Ödenmemiş faturalar"""
    with get_db() as conn:
        cur = get_cursor(conn)

        cur.execute("""
            SELECT 
                i.*,
                s.subscriber_code,
                s.name as subscriber_name,
                CURRENT_DATE - i.due_date as overdue_days
            FROM invoices i
            JOIN subscribers s ON i.subscriber_id = s.id
            WHERE i.status IN ('draft', 'issued')
            ORDER BY i.due_date ASC
        """)

        return [dict(row) for row in cur.fetchall()]


def create_scheduled_reading(meter_id, scheduled_time):
    """Okuma zamanla"""
    with get_db() as conn:
        cur = get_cursor(conn)

        cur.execute(
            """
            INSERT INTO scheduled_readings (meter_id, scheduled_time, status)
            VALUES (%s, %s, 'pending')
            RETURNING id, meter_id, scheduled_time, status
        """,
            (meter_id, scheduled_time),
        )

        return dict(cur.fetchone())


def get_scheduled_readings(status=None):
    """Zamanlanmış okumalar"""
    with get_db() as conn:
        cur = get_cursor(conn)

        query = """
            SELECT 
                sr.*,
                m.meter_no,
                s.name as subscriber_name
            FROM scheduled_readings sr
            JOIN meters m ON sr.meter_id = m.id
            JOIN subscribers s ON m.subscriber_id = s.id
            WHERE 1=1
        """
        params = []

        if status:
            query += " AND sr.status = %s"
            params.append(status)

        query += " ORDER BY sr.scheduled_time DESC"

        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]


def execute_scheduled_reading(scheduled_id):
    """Zamanlanmış okumayı çalıştır (Demo)"""
    with get_db() as conn:
        cur = get_cursor(conn)

        # Zamanlanmış okumayı al
        cur.execute(
            """
            SELECT * FROM scheduled_readings WHERE id = %s
        """,
            (scheduled_id,),
        )

        scheduled = cur.fetchone()
        if not scheduled:
            raise ValueError("Zamanlanmış okuma bulunamadı")

        # Demo: Okuma başarılı olarak işaretle
        cur.execute(
            """
            UPDATE scheduled_readings
            SET status = 'completed', executed_at = NOW()
            WHERE id = %s
            RETURNING *
        """,
            (scheduled_id,),
        )

        return dict(cur.fetchone())


def bulk_start_readings(meter_ids):
    """Toplu okuma başlat"""
    return start_bulk_reading(meter_ids)


def get_subscriber_invoices(subscriber_id):
    """Abone faturaları"""
    with get_db() as conn:
        cur = get_cursor(conn)

        cur.execute(
            """
            SELECT 
                i.*,
                bp.period_name
            FROM invoices i
            JOIN billing_periods bp ON i.period_id = bp.id
            WHERE i.subscriber_id = %s
            ORDER BY i.invoice_date DESC
        """,
            (subscriber_id,),
        )

        return [dict(row) for row in cur.fetchall()]


def create_alarm(source, severity, message):
    """Alarm oluştur"""
    with get_db() as conn:
        cur = get_cursor(conn)

        cur.execute(
            """
            INSERT INTO alarms (source, severity, message, acknowledged, created_at)
            VALUES (%s, %s, %s, FALSE, NOW())
            RETURNING id, source, severity, message, acknowledged, created_at
        """,
            (source, severity, message),
        )

        return dict(cur.fetchone())


def acknowledge_alarm(alarm_id):
    """Alarm onaylama"""
    with get_db() as conn:
        cur = get_cursor(conn)

        cur.execute(
            """
            UPDATE alarms
            SET acknowledged = TRUE, acknowledged_at = NOW()
            WHERE id = %s
            RETURNING *
        """,
            (alarm_id,),
        )

        result = cur.fetchone()
        if not result:
            raise ValueError("Alarm bulunamadı")

        return dict(result)


def export_to_excel(report_type):
    """Excel export (Demo - gerçek implementasyon gerekli)"""
    import tempfile
    import os

    # Demo: Geçici dosya oluştur
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".xlsx", delete=False)
    temp_file.write("Excel export - Implementation needed")
    temp_file.close()

    return temp_file.name


def export_to_pdf(report_type):
    """PDF export (Demo - gerçek implementasyon gerekli)"""
    import tempfile
    import os

    # Demo: Geçici dosya oluştur
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".pdf", delete=False)
    temp_file.write("PDF export - Implementation needed")
    temp_file.close()

    return temp_file.name

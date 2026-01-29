"""
EFYS Database Service
PostgreSQL bağlantısı ve sorgular
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from datetime import datetime, timedelta
from decimal import Decimal
import os

# Database URL
DATABASE_URL = os.environ.get('DATABASE_URL') or \
    'postgresql://postgres:518518Erkan@localhost:5432/osos_db'


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
# DASHBOARD QUERIES
# =============================================================================

def get_dashboard_stats():
    """Dashboard için özet istatistikler - Gerçek metrikler"""
    with get_db() as conn:
        cur = get_cursor(conn)
        
        # Toplam abone ve aktif sayısı
        cur.execute("""
            SELECT 
                COUNT(*) as total_subscribers,
                COUNT(*) FILTER (WHERE status = 'Aktif') as active_subscribers
            FROM subscribers
        """)
        subs = cur.fetchone()
        
        # Bu ayki toplam tüketim ve okuma sayısı
        cur.execute("""
            SELECT 
                COALESCE(SUM(total_consumption), 0)::bigint as monthly_consumption,
                COUNT(*) as reading_count
            FROM readings
            WHERE reading_time >= DATE_TRUNC('month', CURRENT_DATE)
        """)
        consumption = cur.fetchone()
        
        # Sayaç sayısı (aktif/toplam)
        cur.execute("""
            SELECT 
                COUNT(*) as total_meters,
                COUNT(*) FILTER (WHERE status = 'active') as active_meters
            FROM meters
        """)
        meters = cur.fetchone()
        
        # Fatura sayısı (bu ay kesilen)
        cur.execute("""
            SELECT 
                COUNT(*) as invoice_count,
                COALESCE(SUM(total_amount), 0)::numeric as invoice_amount
            FROM invoices
            WHERE issue_date >= DATE_TRUNC('month', CURRENT_DATE)
        """)
        invoices = cur.fetchone()
        
        return {
            'total_subscribers': subs['total_subscribers'],
            'active_subscribers': subs['active_subscribers'],
            'monthly_consumption': consumption['monthly_consumption'],
            'reading_count': consumption['reading_count'],
            'total_meters': meters['total_meters'],
            'active_meters': meters['active_meters'],
            'invoice_count': invoices['invoice_count'],
            'invoice_amount': float(invoices['invoice_amount'] or 0)
        }


def get_daily_consumption_chart(days=7):
    """Son N günlük tüketim grafiği verisi"""
    with get_db() as conn:
        cur = get_cursor(conn)
        
        cur.execute("""
            SELECT 
                DATE(reading_time) as tarih,
                SUM(t1_consumption)::int as t1,
                SUM(t2_consumption)::int as t2,
                SUM(t3_consumption)::int as t3,
                SUM(total_consumption)::int as toplam
            FROM readings
            WHERE reading_time >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY DATE(reading_time)
            ORDER BY tarih
        """, (days,))
        
        results = cur.fetchall()
        
        return {
            'labels': [r['tarih'].strftime('%d.%m') for r in results],
            't1': [r['t1'] for r in results],
            't2': [r['t2'] for r in results],
            't3': [r['t3'] for r in results],
            'toplam': [r['toplam'] for r in results]
        }


def get_reactive_status():
    """Reaktif enerji durumu (endüktif/kapasitif oranı)"""
    with get_db() as conn:
        cur = get_cursor(conn)
        
        cur.execute("""
            SELECT 
                SUM(inductive_reactive)::numeric as enduktif,
                SUM(capacitive_reactive)::numeric as kapasitif,
                AVG(power_factor)::numeric as ortalama_cos_phi
            FROM readings
            WHERE reading_time >= DATE_TRUNC('month', CURRENT_DATE)
        """)
        
        result = cur.fetchone()
        total = float(result['enduktif'] or 0) + float(result['kapasitif'] or 0)
        
        # Count subscribers by reactive type
        cur.execute("""
            SELECT 
                COUNT(DISTINCT CASE WHEN r.inductive_reactive > r.capacitive_reactive THEN m.subscriber_id END) as enduktif_abone,
                COUNT(DISTINCT CASE WHEN r.capacitive_reactive > r.inductive_reactive THEN m.subscriber_id END) as kapasitif_abone,
                COUNT(DISTINCT CASE WHEN r.power_factor < 0.9 THEN m.subscriber_id END) as ceza_riski
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            WHERE r.reading_time >= DATE_TRUNC('month', CURRENT_DATE)
        """)
        abone_result = cur.fetchone()
        
        enduktif_val = float(result['enduktif'] or 0)
        kapasitif_val = float(result['kapasitif'] or 0)
        
        return {
            'enduktif': enduktif_val,
            'kapasitif': kapasitif_val,
            'enduktif_oran': round(enduktif_val / total * 100, 1) if total > 0 else 0,
            'kapasitif_oran': round(kapasitif_val / total * 100, 1) if total > 0 else 0,
            'ortalama_cos_phi': round(float(result['ortalama_cos_phi'] or 0.9), 3),
            'enduktif_abone': int(abone_result['enduktif_abone'] or 0),
            'kapasitif_abone': int(abone_result['kapasitif_abone'] or 0),
            'ceza_riski': int(abone_result['ceza_riski'] or 0)
        }


def get_top_consumers(limit=5):
    """En yüksek tüketimli aboneler"""
    with get_db() as conn:
        cur = get_cursor(conn)
        
        cur.execute("""
            SELECT 
                s.subscriber_code,
                s.name,
                s.sector,
                SUM(r.total_consumption)::int as toplam_tuketim
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            JOIN subscribers s ON m.subscriber_id = s.id
            WHERE r.reading_time >= DATE_TRUNC('month', CURRENT_DATE)
            GROUP BY s.id, s.subscriber_code, s.name, s.sector
            ORDER BY toplam_tuketim DESC
            LIMIT %s
        """, (limit,))
        
        return cur.fetchall()


# =============================================================================
# SUBSCRIBER QUERIES
# =============================================================================

def get_subscribers(page=1, per_page=25, search=None, sector=None):
    """Abone listesi (sayfalama ile)"""
    with get_db() as conn:
        cur = get_cursor(conn)
        
        # Base query
        query = """
            SELECT 
                s.*,
                m.meter_no,
                m.status as meter_status,
                sda.avg_daily_consumption_kwh
            FROM subscribers s
            LEFT JOIN meters m ON s.id = m.subscriber_id
            LEFT JOIN subscriber_daily_averages sda ON s.id = sda.subscriber_id
            WHERE 1=1
        """
        params = []
        
        if search:
            query += " AND (s.name ILIKE %s OR s.subscriber_code ILIKE %s)"
            params.extend([f'%{search}%', f'%{search}%'])
        
        if sector:
            query += " AND s.sector = %s"
            params.append(sector)
        
        # Count total
        count_query = f"SELECT COUNT(*) as total FROM ({query}) sub"
        cur.execute(count_query, params)
        total = cur.fetchone()['total']
        
        # Pagination
        offset = (page - 1) * per_page
        query += " ORDER BY s.subscriber_code LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        cur.execute(query, params)
        items = cur.fetchall()
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }


def get_subscriber_by_id(subscriber_id):
    """Tek bir abone detayı"""
    with get_db() as conn:
        cur = get_cursor(conn)
        
        cur.execute("""
            SELECT 
                s.*,
                m.meter_no,
                m.brand as meter_brand,
                m.model as meter_model,
                m.status as meter_status,
                m.last_reading_at,
                sda.avg_daily_consumption_kwh,
                t.name as tariff_name
            FROM subscribers s
            LEFT JOIN meters m ON s.id = m.subscriber_id
            LEFT JOIN subscriber_daily_averages sda ON s.id = sda.subscriber_id
            LEFT JOIN tariffs t ON s.tariff_id = t.id
            WHERE s.id = %s
        """, (subscriber_id,))
        
        return cur.fetchone()


# =============================================================================
# READINGS QUERIES
# =============================================================================

def get_latest_readings(limit=50):
    """Son okumalar"""
    with get_db() as conn:
        cur = get_cursor(conn)
        
        cur.execute("""
            SELECT 
                r.reading_time,
                m.meter_no,
                s.name as subscriber_name,
                r.t1_index,
                r.t2_index,
                r.t3_index,
                r.total_consumption,
                r.power_factor,
                r.reading_status
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            JOIN subscribers s ON m.subscriber_id = s.id
            ORDER BY r.reading_time DESC
            LIMIT %s
        """, (limit,))
        
        return cur.fetchall()


def get_readings_by_meter(meter_id, start_date=None, end_date=None):
    """Belirli bir sayacın okumaları"""
    with get_db() as conn:
        cur = get_cursor(conn)
        
        query = """
            SELECT 
                reading_time,
                t1_index, t2_index, t3_index,
                t1_consumption, t2_consumption, t3_consumption,
                total_consumption,
                inductive_reactive, capacitive_reactive,
                power_factor, max_demand,
                reading_status
            FROM readings
            WHERE meter_id = %s
        """
        params = [meter_id]
        
        if start_date:
            query += " AND reading_time >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND reading_time <= %s"
            params.append(end_date)
        
        query += " ORDER BY reading_time DESC LIMIT 500"
        
        cur.execute(query, params)
        return cur.fetchall()


# =============================================================================
# TARIFF QUERIES
# =============================================================================

def get_tariffs():
    """Aktif tarifeler"""
    with get_db() as conn:
        cur = get_cursor(conn)
        
        cur.execute("""
            SELECT * FROM tariffs
            WHERE is_active = TRUE
            ORDER BY tariff_type
        """)
        
        return cur.fetchall()


def get_tariff_by_id(tariff_id):
    """Tek tarife"""
    with get_db() as conn:
        cur = get_cursor(conn)
        
        cur.execute("SELECT * FROM tariffs WHERE id = %s", (tariff_id,))
        return cur.fetchone()


# =============================================================================
# BILLING QUERIES
# =============================================================================

def get_billing_periods():
    """Fatura dönemleri"""
    with get_db() as conn:
        cur = get_cursor(conn)
        
        cur.execute("""
            SELECT * FROM billing_periods
            ORDER BY period_start DESC
        """)
        
        return cur.fetchall()


def calculate_invoice(subscriber_id, period_id):
    """Bir abone için fatura hesapla"""
    with get_db() as conn:
        cur = get_cursor(conn)
        
        # Dönem bilgilerini al
        cur.execute("SELECT * FROM billing_periods WHERE id = %s", (period_id,))
        period = cur.fetchone()
        
        # Abone ve tarife bilgilerini al
        cur.execute("""
            SELECT s.*, t.* 
            FROM subscribers s
            JOIN tariffs t ON s.tariff_id = t.id
            WHERE s.id = %s
        """, (subscriber_id,))
        subscriber = cur.fetchone()
        
        # Sayaç ID'sini al
        cur.execute("SELECT id FROM meters WHERE subscriber_id = %s", (subscriber_id,))
        meter = cur.fetchone()
        
        if not meter:
            return None
        
        # Dönem tüketimini hesapla
        cur.execute("""
            SELECT 
                SUM(t1_consumption) as t1,
                SUM(t2_consumption) as t2,
                SUM(t3_consumption) as t3,
                SUM(total_consumption) as total,
                SUM(inductive_reactive) as inductive,
                SUM(capacitive_reactive) as capacitive
            FROM readings
            WHERE meter_id = %s
            AND reading_time BETWEEN %s AND %s
        """, (meter['id'], period['period_start'], period['period_end']))
        
        consumption = cur.fetchone()
        
        # Tutarları hesapla
        t1_amount = float(consumption['t1'] or 0) * float(subscriber['t1_rate'])
        t2_amount = float(consumption['t2'] or 0) * float(subscriber['t2_rate'])
        t3_amount = float(consumption['t3'] or 0) * float(subscriber['t3_rate'])
        
        # Reaktif ceza hesabı (cos phi < 0.9 ise)
        reactive_amount = 0
        total_reactive = float(consumption['inductive'] or 0) + float(consumption['capacitive'] or 0)
        active_total = float(consumption['total'] or 0)
        if active_total > 0:
            tan_phi = total_reactive / active_total
            if tan_phi > 0.484:  # cos phi < 0.9
                excess = total_reactive - (active_total * 0.484)
                reactive_amount = excess * float(subscriber['reactive_rate'])
        
        subtotal = t1_amount + t2_amount + t3_amount + reactive_amount
        vat_amount = subtotal * 0.20
        total_amount = subtotal + vat_amount
        
        return {
            'subscriber': subscriber,
            'period': period,
            'consumption': consumption,
            't1_amount': round(t1_amount, 2),
            't2_amount': round(t2_amount, 2),
            't3_amount': round(t3_amount, 2),
            'reactive_amount': round(reactive_amount, 2),
            'subtotal': round(subtotal, 2),
            'vat_amount': round(vat_amount, 2),
            'total_amount': round(total_amount, 2)
        }


# =============================================================================
# MONITORING QUERIES
# =============================================================================

def get_meter_status_summary():
    """Sayaç durum özeti"""
    with get_db() as conn:
        cur = get_cursor(conn)
        
        cur.execute("""
            SELECT 
                status,
                COUNT(*) as count
            FROM meters
            GROUP BY status
        """)
        
        return cur.fetchall()


def get_hourly_consumption_profile(date=None):
    """Saatlik tüketim profili"""
    if date is None:
        date = datetime.now().date()
    
    with get_db() as conn:
        cur = get_cursor(conn)
        
        cur.execute("""
            SELECT 
                EXTRACT(hour FROM reading_time)::int as saat,
                SUM(total_consumption)::int as tuketim
            FROM readings
            WHERE DATE(reading_time) = %s
            GROUP BY EXTRACT(hour FROM reading_time)
            ORDER BY saat
        """, (date,))
        
        return cur.fetchall()


# =============================================================================
# DATABASE SERVICE CLASS (OOP Interface)
# =============================================================================

class DatabaseService:
    """Object-oriented database service"""
    
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
    
    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
    
    def get_subscriber_stats(self):
        """Abone istatistikleri"""
        self.cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'Aktif') as active,
                COUNT(*) FILTER (WHERE status = 'Askıda') as suspended,
                COUNT(*) FILTER (WHERE status = 'Kapalı') as closed
            FROM subscribers
        """)
        return dict(self.cur.fetchone())
    
    def get_all_subscribers(self):
        """Tüm aboneler (AG-Grid için)"""
        self.cur.execute("""
            SELECT 
                s.id,
                s.subscriber_code as subscriber_no,
                s.name,
                s.sector,
                s.status,
                m.meter_no,
                sda.avg_daily_consumption_kwh as avg_daily_kwh
            FROM subscribers s
            LEFT JOIN meters m ON s.id = m.subscriber_id
            LEFT JOIN subscriber_daily_averages sda ON s.id = sda.subscriber_id
            ORDER BY s.subscriber_code
        """)
        return [dict(row) for row in self.cur.fetchall()]
    
    def get_subscriber_detail(self, subscriber_id):
        """Abone detayı"""
        self.cur.execute("""
            SELECT 
                s.*,
                m.meter_no,
                m.brand as meter_brand,
                m.model as meter_model,
                m.status as meter_status,
                m.last_reading_at,
                sda.avg_daily_consumption_kwh,
                t.name as tariff_name
            FROM subscribers s
            LEFT JOIN meters m ON s.id = m.subscriber_id
            LEFT JOIN subscriber_daily_averages sda ON s.id = sda.subscriber_id
            LEFT JOIN tariffs t ON s.tariff_id = t.id
            WHERE s.id = %s
        """, (subscriber_id,))
        result = self.cur.fetchone()
        return dict(result) if result else None
    
    def get_subscriber_consumption(self, subscriber_id, days=30):
        """Abonenin tüketim geçmişi"""
        self.cur.execute("""
            SELECT 
                DATE(r.reading_time) as tarih,
                SUM(r.total_consumption)::int as tuketim
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            WHERE m.subscriber_id = %s
            AND r.reading_time >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY DATE(r.reading_time)
            ORDER BY tarih
        """, (subscriber_id, days))
        return [dict(row) for row in self.cur.fetchall()]
    
    def get_subscriber_readings(self, subscriber_id, limit=10):
        """Abonenin son okumaları"""
        self.cur.execute("""
            SELECT 
                r.reading_time,
                r.t1_consumption, r.t2_consumption, r.t3_consumption,
                r.total_consumption,
                r.power_factor
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            WHERE m.subscriber_id = %s
            ORDER BY r.reading_time DESC
            LIMIT %s
        """, (subscriber_id, limit))
        return [dict(row) for row in self.cur.fetchall()]
    
    def get_tariffs(self):
        """Aktif tarifeler"""
        self.cur.execute("""
            SELECT * FROM tariffs
            WHERE is_active = TRUE
            ORDER BY tariff_type
        """)
        return [dict(row) for row in self.cur.fetchall()]
    
    def get_all_meters(self):
        """Tüm sayaçlar"""
        self.cur.execute("""
            SELECT 
                m.*,
                s.name as subscriber_name,
                s.subscriber_code
            FROM meters m
            LEFT JOIN subscribers s ON m.subscriber_id = s.id
            ORDER BY m.meter_no
        """)
        return [dict(row) for row in self.cur.fetchall()]
    
    def get_dashboard_stats(self):
        """Dashboard istatistikleri"""
        return get_dashboard_stats()
    
    def get_daily_consumption_chart(self, days=7):
        """Günlük tüketim grafiği"""
        return get_daily_consumption_chart(days)
    
    def get_reactive_status(self):
        """Reaktif durum"""
        return get_reactive_status()
    
    def get_billing_periods(self):
        """Fatura dönemleri"""
        self.cur.execute("""
            SELECT * FROM billing_periods
            ORDER BY period_start DESC
        """)
        return [dict(row) for row in self.cur.fetchall()]
    
    def get_readings_history(self, page=1, per_page=50, meter_id=None, start_date=None, end_date=None):
        """Okuma geçmişi (sayfalı)"""
        query = """
            SELECT 
                r.reading_time,
                m.meter_no,
                s.name as subscriber_name,
                r.t1_consumption, r.t2_consumption, r.t3_consumption,
                r.total_consumption,
                r.power_factor,
                r.reading_status
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            JOIN subscribers s ON m.subscriber_id = s.id
            WHERE 1=1
        """
        params = []
        
        if meter_id:
            query += " AND r.meter_id = %s"
            params.append(meter_id)
        
        if start_date:
            query += " AND r.reading_time >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND r.reading_time <= %s"
            params.append(end_date)
        
        query += " ORDER BY r.reading_time DESC LIMIT %s OFFSET %s"
        offset = (page - 1) * per_page
        params.extend([per_page, offset])
        
        self.cur.execute(query, params)
        return [dict(row) for row in self.cur.fetchall()]
    
    # =========================================================================
    # READINGS METHODS
    # =========================================================================
    
    def get_instant_readings(self, limit=30):
        """Anlık okuma verileri"""
        self.cur.execute("""
            SELECT 
                m.meter_no,
                s.name as subscriber_name,
                r.t1_index, r.t2_index, r.t3_index,
                r.total_consumption as power_kw,
                r.power_factor as cos_phi,
                r.reading_status as status,
                r.reading_time
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            JOIN subscribers s ON m.subscriber_id = s.id
            WHERE r.reading_time >= NOW() - INTERVAL '1 hour'
            ORDER BY r.reading_time DESC
            LIMIT %s
        """, (limit,))
        return [dict(row) for row in self.cur.fetchall()]
    
    def get_reading_stats(self):
        """Okuma istatistikleri"""
        self.cur.execute("""
            SELECT 
                COUNT(*) as total_readings,
                COUNT(DISTINCT r.meter_id) as online_meters,
                COUNT(*) FILTER (WHERE reading_status = 'success') as successful,
                COUNT(*) FILTER (WHERE reading_status = 'failed') as failed,
                COUNT(*) FILTER (WHERE reading_status = 'pending') as pending
            FROM readings r
            WHERE r.reading_time >= NOW() - INTERVAL '1 hour'
        """)
        result = self.cur.fetchone()
        total_readings = result['total_readings'] or 0
        divisor = total_readings or 1
        return {
            'total': result['online_meters'] or 0,
            'total_readings': total_readings,
            'successful': result['successful'] or 0,
            'failed': result['failed'] or 0,
            'pending': result['pending'] or 0,
            'success_rate': round((result['successful'] or 0) / divisor * 100, 1)
        }
    
    def get_readings_with_stats(self, limit=50):
        """Okuma geçmişi + istatistikler"""
        stats = self.get_reading_stats()
        
        self.cur.execute("""
            SELECT 
                r.reading_time,
                m.meter_no,
                s.name as subscriber_name,
                r.t1_consumption, r.t2_consumption, r.t3_consumption,
                r.total_consumption,
                r.power_factor,
                r.reading_status
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            JOIN subscribers s ON m.subscriber_id = s.id
            ORDER BY r.reading_time DESC
            LIMIT %s
        """, (limit,))
        
        return {
            'stats': stats,
            'readings': [dict(row) for row in self.cur.fetchall()]
        }
    
    def get_daily_reading_trend(self, days=7):
        """Günlük okuma trendi"""
        self.cur.execute("""
            SELECT 
                DATE(reading_time) as tarih,
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE reading_status = 'success') as success,
                COUNT(*) FILTER (WHERE reading_status = 'failed') as failed
            FROM readings
            WHERE reading_time >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY DATE(reading_time)
            ORDER BY tarih
        """, (days,))
        return [dict(row) for row in self.cur.fetchall()]
    
    # =========================================================================
    # MONITORING METHODS
    # =========================================================================
    
    def get_meter_indexes(self):
        """Son sayaç endeksleri"""
        self.cur.execute("""
            SELECT DISTINCT ON (m.id)
                m.meter_no,
                s.name as subscriber_name,
                r.t1_index, r.t2_index, r.t3_index,
                r.inductive_reactive as reactive,
                r.power_factor as cos_phi,
                m.status,
                r.reading_time,
                TO_CHAR(r.reading_time, 'DD.MM.YYYY HH24:MI:SS') as reading_time_local
            FROM meters m
            JOIN subscribers s ON m.subscriber_id = s.id
            LEFT JOIN readings r ON m.id = r.meter_id
            ORDER BY m.id, r.reading_time DESC
        """)
        return [dict(row) for row in self.cur.fetchall()]
    
    def get_meter_stats(self):
        """Sayaç durumu istatistikleri"""
        self.cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status IN ('online', 'Çevrimiçi', 'aktif', 'Aktif')) as online,
                COUNT(*) FILTER (WHERE status IN ('offline', 'Çevrimdışı', 'pasif', 'Pasif')) as offline
            FROM meters
        """)
        result = self.cur.fetchone()
        total = result['total'] or 1
        return {
            'total': result['total'] or 0,
            'online': result['online'] or 0,
            'offline': result['offline'] or 0,
            'access_rate': round((result['online'] or 0) / total * 100, 1)
        }
    
    def get_load_profile(self, date=None):
        """Saatlik yük profili"""
        if date is None:
            date = datetime.now().date()
        
        self.cur.execute("""
            SELECT 
                EXTRACT(hour FROM reading_time)::int as hour,
                SUM(total_consumption)::int as consumption,
                MAX(max_demand)::int as max_demand,
                AVG(power_factor)::numeric as avg_pf
            FROM readings
            WHERE DATE(reading_time) = %s
            GROUP BY EXTRACT(hour FROM reading_time)
            ORDER BY hour
        """, (date,))
        return [dict(row) for row in self.cur.fetchall()]
    
    def get_demand_stats(self):
        """Demant istatistikleri"""
        self.cur.execute("""
            SELECT 
                MAX(max_demand)::int as max_demand,
                MIN(max_demand)::int as min_demand,
                AVG(max_demand)::int as avg_demand,
                (SELECT EXTRACT(hour FROM reading_time)::int 
                 FROM readings 
                 WHERE max_demand = (SELECT MAX(max_demand) FROM readings WHERE reading_time >= CURRENT_DATE)
                 AND reading_time >= CURRENT_DATE
                 LIMIT 1) as peak_hour
            FROM readings
            WHERE reading_time >= CURRENT_DATE
        """)
        result = self.cur.fetchone()
        avg = result['avg_demand'] or 1
        max_d = result['max_demand'] or 0
        return {
            'max_demand': max_d,
            'min_demand': result['min_demand'] or 0,
            'avg_demand': avg,
            'load_factor': round(avg / max_d * 100, 1) if max_d > 0 else 0,
            'peak_hour': result['peak_hour'] or 0
        }
    
    def get_loss_analysis(self):
        """Kayıp/kaçak analizi"""
        self.cur.execute("""
            SELECT 
                s.id,
                s.subscriber_code,
                s.name,
                s.sector,
                SUM(r.total_consumption)::int as consumption,
                AVG(r.power_factor)::numeric as avg_pf,
                CASE 
                    WHEN AVG(r.power_factor) < 0.85 THEN 'Yüksek Risk'
                    WHEN AVG(r.power_factor) < 0.90 THEN 'Orta Risk'
                    ELSE 'Düşük Risk'
                END as risk_level
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            JOIN subscribers s ON m.subscriber_id = s.id
            WHERE r.reading_time >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY s.id, s.subscriber_code, s.name, s.sector
            ORDER BY avg_pf ASC
            LIMIT 20
        """)
        return [dict(row) for row in self.cur.fetchall()]
    
    def get_vee_data(self):
        """VEE doğrulama verileri"""
        self.cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE reading_status = 'success') as validated,
                COUNT(*) FILTER (WHERE reading_status = 'estimated') as estimated,
                COUNT(*) FILTER (WHERE reading_status = 'pending' OR reading_status = 'failed') as pending_correction
            FROM readings
            WHERE reading_time >= CURRENT_DATE - INTERVAL '7 days'
        """)
        return dict(self.cur.fetchone())
    
    def get_vee_corrections(self, limit=20):
        """Düzeltme bekleyen okumalar"""
        self.cur.execute("""
            SELECT 
                m.meter_no,
                s.name as subscriber_name,
                r.reading_time,
                r.reading_status as issue,
                r.total_consumption as original_value
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            JOIN subscribers s ON m.subscriber_id = s.id
            WHERE r.reading_status IN ('pending', 'failed', 'estimated')
            AND r.reading_time >= CURRENT_DATE - INTERVAL '7 days'
            ORDER BY r.reading_time DESC
            LIMIT %s
        """, (limit,))
        return [dict(row) for row in self.cur.fetchall()]
    
    # =========================================================================
    # REPORTS METHODS
    # =========================================================================
    
    def get_consumption_report(self, start_date=None, end_date=None):
        """Tüketim raporu"""
        if start_date is None:
            start_date = datetime.now().date() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now().date()
        
        # Özet istatistikler
        self.cur.execute("""
            SELECT 
                SUM(total_consumption)::bigint as total,
                SUM(t1_consumption)::bigint as t1,
                SUM(t2_consumption)::bigint as t2,
                SUM(t3_consumption)::bigint as t3
            FROM readings
            WHERE reading_time BETWEEN %s AND %s
        """, (start_date, end_date))
        stats = dict(self.cur.fetchone())
        
        # Günlük trend
        self.cur.execute("""
            SELECT 
                DATE(reading_time) as tarih,
                SUM(total_consumption)::int as consumption
            FROM readings
            WHERE reading_time BETWEEN %s AND %s
            GROUP BY DATE(reading_time)
            ORDER BY tarih
        """, (start_date, end_date))
        daily = [dict(row) for row in self.cur.fetchall()]
        
        # Sektörel dağılım
        self.cur.execute("""
            SELECT 
                s.sector,
                SUM(r.total_consumption)::bigint as consumption
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            JOIN subscribers s ON m.subscriber_id = s.id
            WHERE r.reading_time BETWEEN %s AND %s
            GROUP BY s.sector
            ORDER BY consumption DESC
        """, (start_date, end_date))
        sectors = [dict(row) for row in self.cur.fetchall()]
        
        # Detaylı veri (AG-Grid için)
        self.cur.execute("""
            SELECT 
                s.subscriber_code,
                s.name,
                s.sector,
                SUM(r.t1_consumption)::int as t1,
                SUM(r.t2_consumption)::int as t2,
                SUM(r.t3_consumption)::int as t3,
                SUM(r.total_consumption)::int as total
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            JOIN subscribers s ON m.subscriber_id = s.id
            WHERE r.reading_time BETWEEN %s AND %s
            GROUP BY s.id, s.subscriber_code, s.name, s.sector
            ORDER BY total DESC
        """, (start_date, end_date))
        details = [dict(row) for row in self.cur.fetchall()]
        
        return {
            'stats': stats,
            'daily': daily,
            'sectors': sectors,
            'details': details
        }
    
    def get_invoice_report(self, period=None):
        """Fatura raporu"""
        self.cur.execute("""
            SELECT 
                COUNT(*) as total_invoices,
                SUM(total_amount)::numeric as total_amount,
                COUNT(*) FILTER (WHERE status = 'paid') as paid_count,
                SUM(total_amount) FILTER (WHERE status = 'paid')::numeric as paid_amount,
                COUNT(*) FILTER (WHERE status IN ('issued', 'draft')) as unpaid_count,
                SUM(total_amount) FILTER (WHERE status IN ('issued', 'draft'))::numeric as unpaid_amount
            FROM invoices
        """)
        stats = dict(self.cur.fetchone())
        
        # Aylık fatura trendi
        self.cur.execute("""
            SELECT 
                TO_CHAR(invoice_date, 'YYYY-MM') as month,
                SUM(total_amount)::numeric as amount,
                COUNT(*) as count
            FROM invoices
            WHERE invoice_date >= CURRENT_DATE - INTERVAL '6 months'
            GROUP BY TO_CHAR(invoice_date, 'YYYY-MM')
            ORDER BY month
        """)
        monthly = [dict(row) for row in self.cur.fetchall()]
        
        # Fatura listesi
        self.cur.execute("""
            SELECT 
                i.invoice_no,
                s.subscriber_code,
                s.name,
                i.invoice_date,
                i.due_date,
                i.total_amount,
                i.status
            FROM invoices i
            JOIN subscribers s ON i.subscriber_id = s.id
            ORDER BY i.invoice_date DESC
            LIMIT 50
        """)
        invoices = [dict(row) for row in self.cur.fetchall()]
        
        return {
            'stats': stats,
            'monthly': monthly,
            'invoices': invoices
        }
    
    def get_demand_report(self):
        """Demant raporu"""
        # Günlük max demant trendi
        self.cur.execute("""
            SELECT 
                DATE(reading_time) as tarih,
                MAX(max_demand)::int as max_demand
            FROM readings
            WHERE reading_time >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY DATE(reading_time)
            ORDER BY tarih
        """)
        daily = [dict(row) for row in self.cur.fetchall()]
        
        # Abone bazlı demant
        self.cur.execute("""
            SELECT 
                s.subscriber_code,
                s.name,
                s.sector,
                MAX(r.max_demand)::int as max_demand,
                AVG(r.max_demand)::int as avg_demand,
                s.contract_demand
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            JOIN subscribers s ON m.subscriber_id = s.id
            WHERE r.reading_time >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY s.id, s.subscriber_code, s.name, s.sector, s.contract_demand
            ORDER BY max_demand DESC
        """)
        by_subscriber = [dict(row) for row in self.cur.fetchall()]
        
        return {
            'daily': daily,
            'by_subscriber': by_subscriber
        }
    
    def get_loss_report(self):
        """
        Kayıp raporu - OSB modeli
        Ana sayaç (giriş) vs katılımcı sayaçları (satılan) farkı = teknik kayıp
        """
        # OSB kayıp raporunu kullan
        osb_report = self.get_osb_loss_report()
        
        # Eski API uyumluluğu için format dönüşümü
        monthly = osb_report['monthly']
        
        # Detaylı analiz (abone bazlı)
        details = []
        for sub in osb_report['subscribers']:
            details.append({
                'subscriber_code': sub['subscriber_code'],
                'name': sub['name'],
                'sector': sub['sector'],
                'consumption': sub['consumption'],
                'loss_share': sub['loss_share'],
                'share_percent': sub['share_percent']
            })
        
        return {
            'monthly': monthly,
            'details': details,
            'current': osb_report['current']
        }
    
    def get_reactive_report(self):
        """Reaktif enerji raporu"""
        # Cos phi dağılımı
        self.cur.execute("""
            SELECT 
                CASE 
                    WHEN power_factor >= 0.95 THEN '0.95+'
                    WHEN power_factor >= 0.90 THEN '0.90-0.95'
                    WHEN power_factor >= 0.85 THEN '0.85-0.90'
                    ELSE '<0.85'
                END as pf_range,
                COUNT(*) as count
            FROM readings
            WHERE reading_time >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY pf_range
            ORDER BY pf_range DESC
        """)
        distribution = [dict(row) for row in self.cur.fetchall()]
        
        # Aylık reaktif trend
        self.cur.execute("""
            SELECT 
                TO_CHAR(reading_time, 'YYYY-MM') as month,
                SUM(inductive_reactive)::bigint as inductive,
                SUM(capacitive_reactive)::bigint as capacitive,
                AVG(power_factor)::numeric as avg_pf
            FROM readings
            WHERE reading_time >= CURRENT_DATE - INTERVAL '6 months'
            GROUP BY TO_CHAR(reading_time, 'YYYY-MM')
            ORDER BY month
        """)
        monthly = [dict(row) for row in self.cur.fetchall()]
        
        # Yüksek riskli aboneler
        self.cur.execute("""
            SELECT 
                s.subscriber_code,
                s.name,
                s.sector,
                AVG(r.power_factor)::numeric as avg_pf,
                SUM(r.inductive_reactive)::int as total_reactive,
                SUM(r.inductive_reactive * 0.89)::numeric as penalty_amount
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            JOIN subscribers s ON m.subscriber_id = s.id
            WHERE r.reading_time >= CURRENT_DATE - INTERVAL '30 days'
            AND r.power_factor < 0.90
            GROUP BY s.id, s.subscriber_code, s.name, s.sector
            ORDER BY avg_pf ASC
            LIMIT 20
        """)
        high_risk = [dict(row) for row in self.cur.fetchall()]
        
        return {
            'distribution': distribution,
            'monthly': monthly,
            'high_risk': high_risk
        }
    
    def get_reading_success_report(self):
        """Okuma başarı raporu"""
        # Günlük başarı trendi
        self.cur.execute("""
            SELECT 
                DATE(reading_time) as tarih,
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE reading_status = 'success') as success,
                ROUND(COUNT(*) FILTER (WHERE reading_status = 'success')::numeric / 
                      NULLIF(COUNT(*), 0) * 100, 1) as success_rate
            FROM readings
            WHERE reading_time >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY DATE(reading_time)
            ORDER BY tarih
        """)
        daily = [dict(row) for row in self.cur.fetchall()]
        
        # Hata dağılımı
        self.cur.execute("""
            SELECT 
                reading_status as reason,
                COUNT(*) as count
            FROM readings
            WHERE reading_status != 'success'
            AND reading_time >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY reading_status
            ORDER BY count DESC
        """)
        errors = [dict(row) for row in self.cur.fetchall()]
        
        # Sayaç bazlı başarı
        self.cur.execute("""
            SELECT 
                m.meter_no,
                s.name as subscriber_name,
                COUNT(*) as total_reads,
                COUNT(*) FILTER (WHERE r.reading_status = 'success') as success,
                ROUND(COUNT(*) FILTER (WHERE r.reading_status = 'success')::numeric / 
                      NULLIF(COUNT(*), 0) * 100, 1) as success_rate
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            JOIN subscribers s ON m.subscriber_id = s.id
            WHERE r.reading_time >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY m.id, m.meter_no, s.name
            ORDER BY success_rate ASC
        """)
        by_meter = [dict(row) for row in self.cur.fetchall()]
        
        return {
            'daily': daily,
            'errors': errors,
            'by_meter': by_meter
        }
    
    # =========================================================================
    # BILLING METHODS
    # =========================================================================
    
    def get_all_tariffs(self):
        """Tüm tarifeler (aktif/pasif) - Frontend için uyarlanmış kolonlar"""
        self.cur.execute("""
            SELECT 
                id, name, tariff_type as subscriber_type,
                t1_rate as t1_unit_price, 
                t2_rate as t2_unit_price, 
                t3_rate as t3_unit_price,
                reactive_rate as reactive_unit_price, 
                distribution_fee,
                epdk_limit, is_active,
                valid_from, valid_to
            FROM tariffs
            ORDER BY tariff_type, name
        """)
        return [dict(row) for row in self.cur.fetchall()]
    
    def get_billing_periods_with_stats(self):
        """Fatura dönemleri (istatistikli)"""
        self.cur.execute("""
            SELECT 
                bp.*,
                COUNT(i.id) as invoice_count,
                COALESCE(SUM(i.total_amount), 0)::numeric as total_amount
            FROM billing_periods bp
            LEFT JOIN invoices i ON i.period_id = bp.id
            GROUP BY bp.id
            ORDER BY bp.period_start DESC
        """)
        return [dict(row) for row in self.cur.fetchall()]
    
    # =========================================================================
    # OSB FATURALAMA METODLARI
    # Ana Sayaç vs Katılımcı Sayaçları - Teknik Kayıp Hesaplama
    # =========================================================================
    
    def get_osb_billing_settings(self):
        """OSB faturalama ayarlarını getir (dağıtım bedeli, iletim, vergi oranları)"""
        self.cur.execute("""
            SELECT setting_key, setting_value 
            FROM osb_billing_settings 
            WHERE valid_to IS NULL OR valid_to >= CURRENT_DATE
        """)
        settings = {}
        for row in self.cur.fetchall():
            settings[row['setting_key']] = float(row['setting_value'])
        return settings
    
    def get_main_meter_consumption(self, start_date, end_date):
        """Ana sayaç toplam tüketimi (OSB giriş enerjisi)"""
        self.cur.execute("""
            SELECT 
                COALESCE(SUM(r.t1_consumption), 0)::numeric as t1,
                COALESCE(SUM(r.t2_consumption), 0)::numeric as t2,
                COALESCE(SUM(r.t3_consumption), 0)::numeric as t3,
                COALESCE(SUM(r.total_consumption), 0)::numeric as total,
                COALESCE(SUM(r.inductive_reactive), 0)::numeric as inductive,
                COALESCE(SUM(r.capacitive_reactive), 0)::numeric as capacitive
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            WHERE m.is_main_meter = TRUE
            AND r.reading_time BETWEEN %s AND %s
        """, (start_date, end_date))
        result = self.cur.fetchone()
        return {
            't1': float(result['t1'] or 0),
            't2': float(result['t2'] or 0),
            't3': float(result['t3'] or 0),
            'total': float(result['total'] or 0),
            'inductive': float(result['inductive'] or 0),
            'capacitive': float(result['capacitive'] or 0)
        }
    
    def get_participant_total_consumption(self, start_date, end_date):
        """Katılımcı sayaçlarının toplam tüketimi (satılan enerji)"""
        self.cur.execute("""
            SELECT 
                COALESCE(SUM(r.t1_consumption), 0)::numeric as t1,
                COALESCE(SUM(r.t2_consumption), 0)::numeric as t2,
                COALESCE(SUM(r.t3_consumption), 0)::numeric as t3,
                COALESCE(SUM(r.total_consumption), 0)::numeric as total,
                COALESCE(SUM(r.inductive_reactive), 0)::numeric as inductive,
                COALESCE(SUM(r.capacitive_reactive), 0)::numeric as capacitive
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            WHERE (m.is_main_meter = FALSE OR m.is_main_meter IS NULL)
            AND m.subscriber_id IS NOT NULL
            AND r.reading_time BETWEEN %s AND %s
        """, (start_date, end_date))
        result = self.cur.fetchone()
        return {
            't1': float(result['t1'] or 0),
            't2': float(result['t2'] or 0),
            't3': float(result['t3'] or 0),
            'total': float(result['total'] or 0),
            'inductive': float(result['inductive'] or 0),
            'capacitive': float(result['capacitive'] or 0)
        }
    
    def calculate_technical_loss(self, start_date, end_date):
        """
        Teknik kayıp hesapla: Ana Sayaç - Katılımcı Toplamı
        Returns: dict with input, sold, loss, loss_rate
        """
        main_meter = self.get_main_meter_consumption(start_date, end_date)
        participants = self.get_participant_total_consumption(start_date, end_date)
        
        input_energy = main_meter['total']
        sold_energy = participants['total']
        technical_loss = input_energy - sold_energy
        loss_rate = (technical_loss / input_energy * 100) if input_energy > 0 else 0
        
        return {
            'input': round(input_energy, 3),
            'sold': round(sold_energy, 3),
            'loss': round(max(0, technical_loss), 3),  # Negatif kayıp olamaz
            'loss_rate': round(loss_rate, 2),
            'main_meter': main_meter,
            'participants': participants
        }
    
    def get_subscriber_loss_share(self, subscriber_id, start_date, end_date):
        """
        Abonenin teknik kayıp payını hesapla
        Formül: (Abone Tüketimi / Toplam Katılımcı Tüketimi) x Toplam Teknik Kayıp
        """
        # Abone tüketimi
        self.cur.execute("""
            SELECT COALESCE(SUM(r.total_consumption), 0)::numeric as total
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            WHERE m.subscriber_id = %s
            AND r.reading_time BETWEEN %s AND %s
        """, (subscriber_id, start_date, end_date))
        subscriber_consumption = float(self.cur.fetchone()['total'] or 0)
        
        # Teknik kayıp bilgileri
        loss_data = self.calculate_technical_loss(start_date, end_date)
        
        # Payı hesapla
        if loss_data['sold'] > 0:
            share_ratio = subscriber_consumption / loss_data['sold']
            loss_share = loss_data['loss'] * share_ratio
        else:
            share_ratio = 0
            loss_share = 0
        
        return {
            'subscriber_consumption': round(subscriber_consumption, 3),
            'share_ratio': round(share_ratio, 4),
            'loss_share_kwh': round(loss_share, 3),
            'total_loss': loss_data['loss'],
            'loss_rate': loss_data['loss_rate']
        }
    
    def calculate_osb_invoice(self, subscriber_id, period_id):
        """
        OSB modeline göre fatura hesapla
        Kalemler:
        1. Aktif Enerji Bedeli (T1/T2/T3)
        2. Dağıtım Bedeli
        3. Teknik Kayıp Payı
        4. İletim Bedeli (TEİAŞ)
        5. Reaktif Ceza
        6. BTV (Belediye Tüketim Vergisi)
        7. KDV
        """
        # Dönem bilgileri
        self.cur.execute("SELECT * FROM billing_periods WHERE id = %s", (period_id,))
        period = self.cur.fetchone()
        if not period:
            return None
        
        # Abone ve tarife bilgileri
        self.cur.execute("""
            SELECT s.*, t.t1_rate, t.t2_rate, t.t3_rate, t.reactive_rate, t.distribution_fee,
                   t.name as tariff_name
            FROM subscribers s
            JOIN tariffs t ON s.tariff_id = t.id
            WHERE s.id = %s
        """, (subscriber_id,))
        subscriber = self.cur.fetchone()
        if not subscriber:
            return None
        
        # Sayaç bilgisi
        self.cur.execute("SELECT id FROM meters WHERE subscriber_id = %s", (subscriber_id,))
        meter = self.cur.fetchone()
        if not meter:
            return None
        
        # OSB ayarları
        settings = self.get_osb_billing_settings()
        
        # Abone dönem tüketimi
        self.cur.execute("""
            SELECT 
                COALESCE(SUM(t1_consumption), 0)::numeric as t1,
                COALESCE(SUM(t2_consumption), 0)::numeric as t2,
                COALESCE(SUM(t3_consumption), 0)::numeric as t3,
                COALESCE(SUM(total_consumption), 0)::numeric as total,
                COALESCE(SUM(inductive_reactive), 0)::numeric as inductive,
                COALESCE(SUM(capacitive_reactive), 0)::numeric as capacitive
            FROM readings
            WHERE meter_id = %s
            AND reading_time BETWEEN %s AND %s
        """, (meter['id'], period['period_start'], period['period_end']))
        consumption = self.cur.fetchone()
        
        t1 = float(consumption['t1'] or 0)
        t2 = float(consumption['t2'] or 0)
        t3 = float(consumption['t3'] or 0)
        total = float(consumption['total'] or 0)
        inductive = float(consumption['inductive'] or 0)
        capacitive = float(consumption['capacitive'] or 0)
        
        # 1. Aktif Enerji Bedeli
        t1_amount = t1 * float(subscriber['t1_rate'])
        t2_amount = t2 * float(subscriber['t2_rate'])
        t3_amount = t3 * float(subscriber['t3_rate'])
        energy_amount = t1_amount + t2_amount + t3_amount
        
        # 2. Dağıtım Bedeli
        distribution_rate = settings.get('distribution_fee_rate', 0.25)
        distribution_amount = total * distribution_rate
        
        # 3. Teknik Kayıp Payı
        loss_share = self.get_subscriber_loss_share(subscriber_id, period['period_start'], period['period_end'])
        loss_share_kwh = loss_share['loss_share_kwh']
        # Kayıp payı maliyeti = Kayıp kWh x Ortalama enerji fiyatı
        avg_rate = (float(subscriber['t1_rate']) + float(subscriber['t2_rate']) + float(subscriber['t3_rate'])) / 3
        technical_loss_amount = loss_share_kwh * avg_rate
        
        # 4. İletim Bedeli (TEİAŞ)
        transmission_rate = settings.get('transmission_fee_rate', 0.035)
        transmission_amount = total * transmission_rate
        
        # 5. Reaktif Ceza
        reactive_amount = 0
        cos_phi_limit = settings.get('cos_phi_limit', 0.90)
        total_reactive = inductive + capacitive
        if total > 0:
            tan_phi = total_reactive / total
            tan_phi_limit = 0.484  # tan(arccos(0.9))
            if tan_phi > tan_phi_limit:
                excess = total_reactive - (total * tan_phi_limit)
                reactive_penalty_rate = settings.get('reactive_penalty_rate', 0.89)
                reactive_amount = excess * reactive_penalty_rate
        
        # Ara toplam (vergiler hariç)
        subtotal = energy_amount + distribution_amount + technical_loss_amount + transmission_amount + reactive_amount
        
        # 6. BTV (Belediye Tüketim Vergisi)
        btv_rate = settings.get('btv_rate', 0.05)
        btv_amount = subtotal * btv_rate
        
        # 7. KDV
        kdv_rate = settings.get('kdv_rate', 0.20)
        kdv_amount = (subtotal + btv_amount) * kdv_rate
        
        # Genel toplam
        total_amount = subtotal + btv_amount + kdv_amount
        
        return {
            'subscriber': dict(subscriber),
            'period': dict(period),
            'meter_id': meter['id'],
            'consumption': {
                't1': round(t1, 3),
                't2': round(t2, 3),
                't3': round(t3, 3),
                'total': round(total, 3),
                'inductive': round(inductive, 3),
                'capacitive': round(capacitive, 3)
            },
            # Tutarlar
            't1_amount': round(t1_amount, 2),
            't2_amount': round(t2_amount, 2),
            't3_amount': round(t3_amount, 2),
            'energy_amount': round(energy_amount, 2),
            'distribution_amount': round(distribution_amount, 2),
            'technical_loss_share': round(loss_share_kwh, 3),
            'technical_loss_amount': round(technical_loss_amount, 2),
            'transmission_amount': round(transmission_amount, 2),
            'reactive_amount': round(reactive_amount, 2),
            'subtotal': round(subtotal, 2),
            'btv_rate': btv_rate,
            'btv_amount': round(btv_amount, 2),
            'kdv_rate': kdv_rate,
            'kdv_amount': round(kdv_amount, 2),
            'total_amount': round(total_amount, 2),
            # Ek bilgiler
            'loss_info': loss_share,
            'settings': settings
        }
    
    def get_osb_loss_report(self):
        """
        OSB kayıp raporu - Ana sayaç vs Aboneler
        Aylık trend ve güncel durum
        """
        # Son 6 aylık aylık bazda kayıp trendi
        self.cur.execute("""
            WITH monthly_main AS (
                SELECT 
                    TO_CHAR(r.reading_time, 'YYYY-MM') as month,
                    SUM(r.total_consumption)::bigint as input
                FROM readings r
                JOIN meters m ON r.meter_id = m.id
                WHERE m.is_main_meter = TRUE
                AND r.reading_time >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY TO_CHAR(r.reading_time, 'YYYY-MM')
            ),
            monthly_participants AS (
                SELECT 
                    TO_CHAR(r.reading_time, 'YYYY-MM') as month,
                    SUM(r.total_consumption)::bigint as sold
                FROM readings r
                JOIN meters m ON r.meter_id = m.id
                WHERE (m.is_main_meter = FALSE OR m.is_main_meter IS NULL)
                AND m.subscriber_id IS NOT NULL
                AND r.reading_time >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY TO_CHAR(r.reading_time, 'YYYY-MM')
            )
            SELECT 
                mm.month,
                COALESCE(mm.input, 0) as input,
                COALESCE(mp.sold, 0) as sold,
                COALESCE(mm.input, 0) - COALESCE(mp.sold, 0) as loss,
                CASE WHEN COALESCE(mm.input, 0) > 0 
                     THEN ROUND(((COALESCE(mm.input, 0) - COALESCE(mp.sold, 0))::numeric / 
                                  COALESCE(mm.input, 0) * 100), 2)
                     ELSE 0 
                END as loss_rate
            FROM monthly_main mm
            LEFT JOIN monthly_participants mp ON mm.month = mp.month
            ORDER BY mm.month
        """)
        monthly = [dict(row) for row in self.cur.fetchall()]
        
        # Güncel kayıp durumu (son 30 gün)
        current_loss = self.calculate_technical_loss(
            datetime.now().date() - timedelta(days=30),
            datetime.now().date()
        )
        
        # Abone bazlı kayıp payları
        self.cur.execute("""
            SELECT 
                s.id,
                s.subscriber_code,
                s.name,
                s.sector,
                COALESCE(SUM(r.total_consumption), 0)::bigint as consumption
            FROM subscribers s
            JOIN meters m ON m.subscriber_id = s.id
            JOIN readings r ON r.meter_id = m.id
            WHERE r.reading_time >= CURRENT_DATE - INTERVAL '30 days'
            AND (m.is_main_meter = FALSE OR m.is_main_meter IS NULL)
            GROUP BY s.id, s.subscriber_code, s.name, s.sector
            ORDER BY consumption DESC
        """)
        subscribers = [dict(row) for row in self.cur.fetchall()]
        
        # Her aboneye kayıp payını ekle
        total_participant = current_loss['sold']
        total_loss = current_loss['loss']
        for sub in subscribers:
            if total_participant > 0:
                share_ratio = sub['consumption'] / total_participant
                sub['loss_share'] = round(total_loss * share_ratio, 3)
                sub['share_percent'] = round(share_ratio * 100, 2)
            else:
                sub['loss_share'] = 0
                sub['share_percent'] = 0
        
        return {
            'monthly': monthly,
            'current': current_loss,
            'subscribers': subscribers
        }

    # ============================================================
    # PORTAL (SANAYİCİ) FONKSİYONLARI
    # ============================================================
    
    def get_portal_subscriber_data(self, subscriber_id):
        """Portal için abone bilgisi"""
        self.cur.execute("""
            SELECT 
                s.id,
                s.subscriber_code as code,
                s.name,
                s.sector,
                s.address,
                s.phone,
                s.email,
                s.contract_demand,
                m.meter_no,
                m.brand,
                m.model
            FROM subscribers s
            LEFT JOIN meters m ON m.subscriber_id = s.id
            WHERE s.id = %s
        """, (subscriber_id,))
        result = self.cur.fetchone()
        return dict(result) if result else None
    
    def get_portal_consumption_data(self, subscriber_id):
        """Portal için tüketim özeti (bu ay ve karşılaştırma)"""
        self.cur.execute("""
            WITH this_month AS (
                SELECT 
                    COALESCE(SUM(r.total_consumption), 0) as total_kwh,
                    COALESCE(SUM(r.t1_consumption), 0) as t1,
                    COALESCE(SUM(r.t2_consumption), 0) as t2,
                    COALESCE(SUM(r.t3_consumption), 0) as t3
                FROM readings r
                JOIN meters m ON r.meter_id = m.id
                WHERE m.subscriber_id = %s
                AND r.reading_time >= DATE_TRUNC('month', CURRENT_DATE)
            ),
            last_month AS (
                SELECT 
                    COALESCE(SUM(r.total_consumption), 0) as total_kwh
                FROM readings r
                JOIN meters m ON r.meter_id = m.id
                WHERE m.subscriber_id = %s
                AND r.reading_time >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month'
                AND r.reading_time < DATE_TRUNC('month', CURRENT_DATE)
            )
            SELECT 
                tm.total_kwh,
                tm.t1, tm.t2, tm.t3,
                lm.total_kwh as last_month_kwh,
                CASE 
                    WHEN lm.total_kwh > 0 
                    THEN ROUND(((tm.total_kwh - lm.total_kwh) / lm.total_kwh * 100)::numeric, 1)
                    ELSE 0 
                END as consumption_change
            FROM this_month tm, last_month lm
        """, (subscriber_id, subscriber_id))
        result = self.cur.fetchone()
        
        if result:
            data = dict(result)
            # Tahmini fatura hesapla (basit)
            data['estimated_bill'] = float(data['total_kwh']) * 3.5  # Ortalama birim fiyat
            data['bill_change'] = float(data['consumption_change'] or 0)
            return data
        return {
            'total_kwh': 0, 't1': 0, 't2': 0, 't3': 0,
            'estimated_bill': 0, 'bill_change': 0, 'consumption_change': 0
        }
    
    def get_portal_reactive_data(self, subscriber_id):
        """Portal için reaktif enerji durumu"""
        self.cur.execute("""
            SELECT 
                COALESCE(SUM(r.total_consumption), 0) as active,
                COALESCE(SUM(r.inductive_reactive), 0) as inductive,
                COALESCE(SUM(r.capacitive_reactive), 0) as capacitive
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            WHERE m.subscriber_id = %s
            AND r.reading_time >= DATE_TRUNC('month', CURRENT_DATE)
        """, (subscriber_id,))
        result = self.cur.fetchone()
        
        if result:
            active = float(result['active']) or 1
            inductive = float(result['inductive']) or 0
            capacitive = float(result['capacitive']) or 0
            
            return {
                'active_kwh': active,
                'inductive_kvarh': inductive,
                'capacitive_kvarh': capacitive,
                'inductive_ratio': round(inductive / active * 100, 1) if active > 0 else 0,
                'capacitive_ratio': round(capacitive / active * 100, 1) if active > 0 else 0,
                'cos_phi': round(active / ((active**2 + inductive**2)**0.5), 3) if active > 0 else 1.0
            }
        return {
            'active_kwh': 0, 'inductive_kvarh': 0, 'capacitive_kvarh': 0,
            'inductive_ratio': 0, 'capacitive_ratio': 0, 'cos_phi': 1.0
        }
    
    def get_portal_invoices(self, subscriber_id, limit=10):
        """Portal için fatura listesi"""
        self.cur.execute("""
            SELECT 
                i.id,
                i.invoice_no,
                i.issue_date as invoice_date,
                i.due_date,
                i.total_amount,
                i.status,
                CASE
                    WHEN i.status = 'issued' AND i.issue_date > CURRENT_DATE THEN 'scheduled'
                    ELSE i.status
                END as display_status,
                bp.name as period_name
            FROM invoices i
            LEFT JOIN billing_periods bp ON i.period_id = bp.id
            WHERE i.subscriber_id = %s
            ORDER BY i.issue_date DESC
            LIMIT %s
        """, (subscriber_id, limit))
        return [dict(row) for row in self.cur.fetchall()]
    
    def get_portal_daily_consumption(self, subscriber_id, days=7):
        """Portal için günlük tüketim grafiği verisi"""
        self.cur.execute("""
            SELECT 
                DATE(r.reading_time) as day,
                SUM(r.total_consumption) as kwh
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            WHERE m.subscriber_id = %s
            AND r.reading_time >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY DATE(r.reading_time)
            ORDER BY day DESC
            LIMIT %s
        """, (subscriber_id, days, days))
        results = [dict(row) for row in self.cur.fetchall()]
        
        # Son N gün için değerleri döndür
        values = []
        for i in range(days):
            found = False
            for r in results:
                if r['day']:
                    found = True
                    values.append(int(r['kwh'] or 0))
                    break
            if not found:
                values.append(0)
        
        # Sadece kWh değerlerini döndür (en yeniden eskiye)
        return [int(r['kwh'] or 0) for r in results][::-1] if results else [0] * days
    
    def get_portal_reactive_history(self, subscriber_id, days=30):
        """Portal için reaktif enerji geçmişi"""
        self.cur.execute("""
            SELECT 
                DATE(r.reading_time) as day,
                SUM(r.total_consumption) as active,
                SUM(r.inductive_reactive) as inductive,
                SUM(r.capacitive_reactive) as capacitive
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            WHERE m.subscriber_id = %s
            AND r.reading_time >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY DATE(r.reading_time)
            ORDER BY day
        """, (subscriber_id, days))
        results = []
        for row in self.cur.fetchall():
            r = dict(row)
            active = float(r['active']) or 1
            r['inductive_ratio'] = round(float(r['inductive'] or 0) / active * 100, 1)
            r['capacitive_ratio'] = round(float(r['capacitive'] or 0) / active * 100, 1)
            results.append(r)
        return results

    # =========================================================================
    # TARIFF MANAGEMENT CRUD OPERATIONS
    # =========================================================================

    def create_tariff(self, tariff_data):
        """Create new energy tariff (T1/T2/T3)"""
        self.cur.execute("""
            INSERT INTO tariffs (
                name, tariff_type, t1_rate, t2_rate, t3_rate, 
                reactive_rate, distribution_fee, epdk_limit, 
                valid_from, valid_to, is_active
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            tariff_data['name'],
            tariff_data['tariff_type'],
            tariff_data['t1_rate'],
            tariff_data['t2_rate'],
            tariff_data['t3_rate'],
            tariff_data.get('reactive_rate', 0.89),
            tariff_data.get('distribution_fee', 0),
            tariff_data.get('epdk_limit', 0.20),
            tariff_data.get('valid_from', '2026-01-01'),
            tariff_data.get('valid_to'),
            tariff_data.get('is_active', True)
        ))
        self.conn.commit()
        return self.cur.fetchone()['id']

    def update_tariff(self, tariff_id, tariff_data):
        """Update existing energy tariff"""
        self.cur.execute("""
            UPDATE tariffs SET
                name = %s,
                tariff_type = %s,
                t1_rate = %s,
                t2_rate = %s,
                t3_rate = %s,
                reactive_rate = %s,
                distribution_fee = %s,
                epdk_limit = %s,
                valid_from = %s,
                valid_to = %s,
                is_active = %s
            WHERE id = %s
        """, (
            tariff_data['name'],
            tariff_data['tariff_type'],
            tariff_data['t1_rate'],
            tariff_data['t2_rate'],
            tariff_data['t3_rate'],
            tariff_data.get('reactive_rate', 0.89),
            tariff_data.get('distribution_fee', 0),
            tariff_data.get('epdk_limit', 0.20),
            tariff_data.get('valid_from', '2026-01-01'),
            tariff_data.get('valid_to'),
            tariff_data.get('is_active', True),
            tariff_id
        ))
        self.conn.commit()
        return self.cur.rowcount > 0

    def delete_tariff(self, tariff_id):
        """Delete energy tariff (soft delete - set is_active=false)"""
        self.cur.execute("UPDATE tariffs SET is_active = false WHERE id = %s", (tariff_id,))
        self.conn.commit()
        return self.cur.rowcount > 0

    def create_osb_distribution_tariff(self, data):
        """Create OSB distribution tariff with tariff_type (tek_terim or dual_term)"""
        self.cur.execute("""
            INSERT INTO osb_distribution_tariffs (
                period_year, tariff_type, og_rate, ag_rate, capacity_rate, 
                energy_rate, is_active, epdk_approved
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data['period_year'],
            data.get('tariff_type', 'dual_term'),  # Default: dual_term
            data['og_rate'],
            data['ag_rate'],
            data.get('capacity_rate', 0),
            data.get('energy_rate', 0),
            data.get('is_active', True),
            data.get('epdk_approved', False)
        ))
        self.conn.commit()
        return self.cur.fetchone()['id']

    def create_edas_tariff(self, data):
        """Create EDAŞ ceiling tariff"""
        self.cur.execute("""
            INSERT INTO edas_tariffs (
                edas_name, period_year, single_term_og_rate, single_term_ag_rate,
                dual_term_capacity_rate, dual_term_energy_rate, 
                valid_from, valid_to, is_active
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data['edas_name'],
            data['period_year'],  # Required field
            data['single_term_og_rate'],
            data['single_term_ag_rate'],
            data.get('dual_term_capacity_rate', 0),
            data.get('dual_term_energy_rate', 0),
            data.get('valid_from', '2026-01-01'),
            data.get('valid_to'),
            data.get('is_active', True)
        ))
        self.conn.commit()
        return self.cur.fetchone()['id']

    def update_billing_settings(self, settings):
        """Update OSB billing settings (key-value pairs)"""
        for key, value in settings.items():
            self.cur.execute("""
                INSERT INTO osb_billing_settings (setting_key, setting_value, valid_from)
                VALUES (%s, %s, CURRENT_DATE)
                ON CONFLICT (setting_key) 
                WHERE valid_to IS NULL
                DO UPDATE SET 
                    setting_value = EXCLUDED.setting_value,
                    valid_from = EXCLUDED.valid_from
            """, (key, str(value)))
        self.conn.commit()
        return True

"""
EFYS Demo Veri Üretici
Gönen OSB - Gerçekçi 15 Dakikalık Okuma Verileri
01.01.2026 - 29.01.2026 (29 gün)

Özellikler:
- Hafta sonu düşük tüketim (%20-30)
- Mesai saatleri yüksek tüketim (08:00-18:00)
- Sektörel farklılıklar (Kimya 24 saat, Gıda gündüz ağırlıklı)
- T1/T2/T3 zaman dilimleri (EPDK)
- Rastgele varyasyon (%10-15)
"""

import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timedelta
from decimal import Decimal
import random
import math

# Database bağlantısı
DB_URL = "postgresql://postgres:518518Erkan@localhost:5432/osos_db"

# EPDK Zaman Dilimleri (Türkiye)
# T1: Gündüz (06:00-17:00)
# T2: Puant (17:00-22:00)
# T3: Gece (22:00-06:00)

def get_time_period(hour):
    """Saate göre zaman dilimi döndür"""
    if 6 <= hour < 17:
        return 'T1'
    elif 17 <= hour < 22:
        return 'T2'
    else:
        return 'T3'

def get_hour_factor(hour, sector):
    """
    Saat ve sektöre göre tüketim faktörü
    Mesai saatleri: 08:00-18:00 yüksek tüketim
    """
    # Sektörel çalışma profilleri
    if sector == 'Kimya':
        # Kimya: 24 saat sürekli çalışır, gece biraz düşük
        if 22 <= hour or hour < 6:
            return 0.85  # Gece %85
        else:
            return 1.0   # Gündüz %100
    
    elif sector == 'Gıda':
        # Gıda: Gündüz ağırlıklı (06:00-20:00)
        if 6 <= hour < 8:
            return 0.6   # Sabah hazırlık
        elif 8 <= hour < 18:
            return 1.2   # Mesai yoğun
        elif 18 <= hour < 20:
            return 0.8   # Akşam azalan
        else:
            return 0.2   # Gece minimal
    
    elif sector == 'Tekstil':
        # Tekstil: 2 vardiya sistemi (06:00-22:00)
        if 6 <= hour < 14:
            return 1.1   # 1. Vardiya
        elif 14 <= hour < 22:
            return 1.0   # 2. Vardiya
        else:
            return 0.15  # Gece bakım
    
    elif sector == 'Deri':
        # Deri: Standart mesai + fazla mesai
        if 8 <= hour < 12:
            return 1.2   # Sabah yoğun
        elif 12 <= hour < 13:
            return 0.5   # Öğle arası
        elif 13 <= hour < 18:
            return 1.1   # Öğleden sonra
        elif 18 <= hour < 20:
            return 0.7   # Fazla mesai
        elif 6 <= hour < 8:
            return 0.4   # Sabah hazırlık
        else:
            return 0.1   # Gece minimal
    
    else:  # Makine vb.
        # Makine: Standart mesai
        if 8 <= hour < 12:
            return 1.15
        elif 12 <= hour < 13:
            return 0.4   # Öğle arası
        elif 13 <= hour < 17:
            return 1.1
        elif 17 <= hour < 18:
            return 0.6   # Paydos
        elif 6 <= hour < 8:
            return 0.3
        else:
            return 0.05

def get_weekend_factor(date, sector):
    """
    Hafta sonu faktörü
    Cumartesi: Yarım mesai veya kapalı
    Pazar: Genellikle kapalı
    """
    weekday = date.weekday()  # 0=Pazartesi, 6=Pazar
    
    if weekday == 5:  # Cumartesi
        if sector == 'Kimya':
            return 0.85  # Kimya hafta sonu da çalışır
        elif sector == 'Gıda':
            return 0.5   # Gıda yarım gün
        else:
            return 0.3   # Diğerleri az çalışır
    
    elif weekday == 6:  # Pazar
        if sector == 'Kimya':
            return 0.75  # Kimya devam eder
        else:
            return 0.1   # Sadece bekçi/güvenlik
    
    return 1.0  # Hafta içi normal

def generate_readings():
    """Ana veri üretim fonksiyonu"""
    
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    # Abone ve ortalama tüketim bilgilerini al
    cur.execute("""
        SELECT m.id as meter_id, m.subscriber_id, s.name, s.sector, 
               sda.avg_daily_consumption_kwh,
               sda.t1_ratio, sda.t2_ratio, sda.t3_ratio
        FROM meters m
        JOIN subscribers s ON m.subscriber_id = s.id
        JOIN subscriber_daily_averages sda ON s.id = sda.subscriber_id
        ORDER BY m.id
    """)
    
    meters = cur.fetchall()
    print(f"Toplam {len(meters)} sayaç için veri üretiliyor...")
    
    # Tarih aralığı
    start_date = datetime(2026, 1, 1, 0, 0)
    end_date = datetime(2026, 1, 29, 23, 45)  # 29 Ocak 23:45'e kadar
    
    # 15 dakikalık aralıklar (günde 96 okuma)
    interval = timedelta(minutes=15)
    
    # Her sayaç için başlangıç endeksleri (rastgele)
    initial_indexes = {}
    for meter in meters:
        meter_id = meter[0]
        # Başlangıç endeksi: 100,000 - 500,000 arası
        initial_indexes[meter_id] = {
            't1': random.uniform(100000, 500000),
            't2': random.uniform(50000, 200000),
            't3': random.uniform(30000, 100000)
        }
    
    all_readings = []
    total_readings = 0
    
    for meter in meters:
        meter_id = meter[0]
        subscriber_id = meter[1]
        name = meter[2]
        sector = meter[3]
        avg_daily = float(meter[4])  # Günlük ortalama kWh
        t1_ratio = float(meter[5])
        t2_ratio = float(meter[6])
        t3_ratio = float(meter[7])
        
        # 15 dakikalık ortalama tüketim (günde 96 okuma)
        base_15min = avg_daily / 96
        
        # Kümülatif endeksler
        t1_index = initial_indexes[meter_id]['t1']
        t2_index = initial_indexes[meter_id]['t2']
        t3_index = initial_indexes[meter_id]['t3']
        
        current_time = start_date
        readings_for_meter = []
        
        while current_time <= end_date:
            hour = current_time.hour
            
            # Faktörleri hesapla
            hour_factor = get_hour_factor(hour, sector)
            weekend_factor = get_weekend_factor(current_time, sector)
            random_factor = random.uniform(0.85, 1.15)  # %15 rastgele varyasyon
            
            # Toplam faktör
            total_factor = hour_factor * weekend_factor * random_factor
            
            # 15 dakikalık tüketim
            consumption_15min = base_15min * total_factor
            
            # Zaman dilimi belirle
            period = get_time_period(hour)
            
            # Tüketime göre T1/T2/T3 dağılımı
            if period == 'T1':
                t1_cons = consumption_15min
                t2_cons = 0
                t3_cons = 0
            elif period == 'T2':
                t1_cons = 0
                t2_cons = consumption_15min
                t3_cons = 0
            else:
                t1_cons = 0
                t2_cons = 0
                t3_cons = consumption_15min
            
            # Endeksleri güncelle
            t1_index += t1_cons
            t2_index += t2_cons
            t3_index += t3_cons
            
            total_cons = t1_cons + t2_cons + t3_cons
            
            # Reaktif enerji (cos_phi = 0.85-0.95 arası)
            cos_phi = random.uniform(0.85, 0.95)
            # tan(arccos(cos_phi)) * active = reactive
            tan_phi = math.sqrt(1 - cos_phi**2) / cos_phi
            inductive = total_cons * tan_phi * 0.9  # %90 endüktif
            capacitive = total_cons * tan_phi * 0.1  # %10 kapasitif
            
            # Max demand (rastgele spike'lar)
            max_demand = (consumption_15min * 4) * random.uniform(0.9, 1.1)  # kW
            
            readings_for_meter.append((
                meter_id,
                current_time,
                round(t1_index, 3),
                round(t2_index, 3),
                round(t3_index, 3),
                round(t1_cons, 3),
                round(t2_cons, 3),
                round(t3_cons, 3),
                round(total_cons, 3),
                round(inductive, 3),
                round(capacitive, 3),
                round(cos_phi, 4),
                round(max_demand, 3),
                'Başarılı'
            ))
            
            current_time += interval
        
        all_readings.extend(readings_for_meter)
        total_readings += len(readings_for_meter)
        print(f"  ✓ {name[:30]:30} - {len(readings_for_meter)} okuma")
    
    print(f"\nToplam {total_readings} okuma veritabanına yazılıyor...")
    
    # Toplu insert (çok daha hızlı)
    insert_query = """
        INSERT INTO readings (
            meter_id, reading_time, t1_index, t2_index, t3_index,
            t1_consumption, t2_consumption, t3_consumption, total_consumption,
            inductive_reactive, capacitive_reactive, power_factor, max_demand,
            reading_status
        ) VALUES %s
    """
    
    # Batch insert (10000'lik gruplar halinde)
    batch_size = 10000
    for i in range(0, len(all_readings), batch_size):
        batch = all_readings[i:i+batch_size]
        execute_values(cur, insert_query, batch)
        print(f"  Yazıldı: {min(i+batch_size, len(all_readings))}/{len(all_readings)}")
    
    conn.commit()
    
    # Sayaç son okuma zamanlarını güncelle
    cur.execute("""
        UPDATE meters m
        SET last_reading_at = (
            SELECT MAX(reading_time) FROM readings r WHERE r.meter_id = m.id
        )
    """)
    conn.commit()
    
    # Özet istatistikler
    cur.execute("""
        SELECT 
            COUNT(*) as toplam_okuma,
            SUM(total_consumption)::bigint as toplam_tuketim_kwh,
            MIN(reading_time) as ilk_okuma,
            MAX(reading_time) as son_okuma
        FROM readings
    """)
    stats = cur.fetchone()
    
    print(f"\n{'='*50}")
    print("DEMO VERİ ÜRETİMİ TAMAMLANDI")
    print(f"{'='*50}")
    print(f"Toplam Okuma: {stats[0]:,}")
    print(f"Toplam Tüketim: {stats[1]:,} kWh ({stats[1]/1000:,.0f} MWh)")
    print(f"İlk Okuma: {stats[2]}")
    print(f"Son Okuma: {stats[3]}")
    
    cur.close()
    conn.close()
    
    return stats

if __name__ == "__main__":
    print("EFYS Demo Veri Üretici")
    print("=" * 50)
    print("Tarih Aralığı: 01.01.2026 - 29.01.2026")
    print("Okuma Aralığı: 15 dakika (günde 96 okuma)")
    print("=" * 50)
    generate_readings()

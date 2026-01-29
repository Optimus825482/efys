"""
EFYS OSB Faturalama Servisi
EPDK Organize Sanayi Bölgeleri Elektrik Dağıtım Bedelleri El Kitabı'na Uygun

Faturalama Akışı:
FAZ 1: Veri Toplama (Ana Sayaç, Katılımcı Sayaçları, Maliyet Verileri)
FAZ 2: Birim Fiyat Belirleme (Enerji Fiyatı, Dağıtım Bedeli, EDAŞ Tavan Kontrolü)
FAZ 3: Fatura Hesaplama (Aktif Enerji, Dağıtım, İletim, Reaktif Ceza, Vergiler)
FAZ 4: Fatura Çıktısı ve Raporlama
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple
import os

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


class OSBBillingService:
    """
    OSB Elektrik Faturalama Servisi
    EPDK mevzuatına tam uyumlu hesaplama
    """
    
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
    
    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
    
    # =========================================================================
    # FAZ 1: VERİ TOPLAMA
    # =========================================================================
    
    def get_main_meter_data(self, start_date, end_date) -> Dict:
        """
        OSB Ana Sayaç verisi - TEİAŞ/Tedarik Şirketi alış noktası
        Giren toplam enerji, reaktif değerler, gelen fatura tutarı
        """
        self.cur.execute("""
            SELECT 
                COALESCE(SUM(r.t1_consumption), 0)::numeric as t1,
                COALESCE(SUM(r.t2_consumption), 0)::numeric as t2,
                COALESCE(SUM(r.t3_consumption), 0)::numeric as t3,
                COALESCE(SUM(r.total_consumption), 0)::numeric as total,
                COALESCE(SUM(r.inductive_reactive), 0)::numeric as inductive,
                COALESCE(SUM(r.capacitive_reactive), 0)::numeric as capacitive,
                COALESCE(MAX(r.max_demand), 0)::numeric as max_demand
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
            'capacitive': float(result['capacitive'] or 0),
            'max_demand': float(result['max_demand'] or 0)
        }
    
    def get_participant_consumption(self, subscriber_id: int, start_date, end_date) -> Dict:
        """
        Katılımcı sayaç verisi - OSOS'tan otomatik okuma
        """
        self.cur.execute("""
            SELECT 
                COALESCE(SUM(r.t1_consumption), 0)::numeric as t1,
                COALESCE(SUM(r.t2_consumption), 0)::numeric as t2,
                COALESCE(SUM(r.t3_consumption), 0)::numeric as t3,
                COALESCE(SUM(r.total_consumption), 0)::numeric as total,
                COALESCE(SUM(r.inductive_reactive), 0)::numeric as inductive,
                COALESCE(SUM(r.capacitive_reactive), 0)::numeric as capacitive,
                COALESCE(MAX(r.max_demand), 0)::numeric as max_demand,
                m.multiplier
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            WHERE m.subscriber_id = %s
            AND r.reading_time BETWEEN %s AND %s
            GROUP BY m.multiplier
        """, (subscriber_id, start_date, end_date))
        result = self.cur.fetchone()
        
        if not result:
            return {
                't1': 0, 't2': 0, 't3': 0, 'total': 0,
                'inductive': 0, 'capacitive': 0, 'max_demand': 0,
                'multiplier': 1.0
            }
        
        multiplier = float(result['multiplier'] or 1.0)
        return {
            't1': float(result['t1'] or 0) * multiplier,
            't2': float(result['t2'] or 0) * multiplier,
            't3': float(result['t3'] or 0) * multiplier,
            'total': float(result['total'] or 0) * multiplier,
            'inductive': float(result['inductive'] or 0) * multiplier,
            'capacitive': float(result['capacitive'] or 0) * multiplier,
            'max_demand': float(result['max_demand'] or 0) * multiplier,
            'multiplier': multiplier
        }
    
    def get_all_participants_total(self, start_date, end_date) -> Dict:
        """
        Tüm katılımcıların toplam tüketimi - Tahakkuk edilen enerji
        """
        self.cur.execute("""
            SELECT 
                COALESCE(SUM(r.total_consumption * m.multiplier), 0)::numeric as total
            FROM readings r
            JOIN meters m ON r.meter_id = m.id
            WHERE (m.is_main_meter = FALSE OR m.is_main_meter IS NULL)
            AND m.subscriber_id IS NOT NULL
            AND r.reading_time BETWEEN %s AND %s
        """, (start_date, end_date))
        result = self.cur.fetchone()
        return {'total': float(result['total'] or 0)}
    
    def get_solar_production(self, subscriber_id: int, start_date, end_date) -> Dict:
        """
        GES (Güneş Enerjisi) üretim verisi - Mahsuplaşma için
        """
        self.cur.execute("""
            SELECT 
                COALESCE(SUM(production_kwh), 0)::numeric as production,
                COALESCE(SUM(exported_kwh), 0)::numeric as exported,
                COALESCE(SUM(self_consumed_kwh), 0)::numeric as self_consumed
            FROM solar_production
            WHERE subscriber_id = %s
            AND reading_time BETWEEN %s AND %s
        """, (subscriber_id, start_date, end_date))
        result = self.cur.fetchone()
        
        return {
            'production': float(result['production'] or 0),
            'exported': float(result['exported'] or 0),
            'self_consumed': float(result['self_consumed'] or 0),
            'has_solar': float(result['production'] or 0) > 0
        }
    
    def get_cost_components(self, year: int) -> Dict:
        """
        OSB işletme giderleri - DGG hesabı için
        """
        self.cur.execute("""
            SELECT * FROM osb_cost_components WHERE period_year = %s
        """, (year,))
        result = self.cur.fetchone()
        
        if not result:
            return None
        return dict(result)
    
    # =========================================================================
    # FAZ 2: BİRİM FİYAT BELİRLEME
    # =========================================================================
    
    def calculate_energy_unit_price(self, start_date, end_date) -> float:
        """
        Aktif Enerji Birim Fiyatı hesaplama
        Formül: Birim Enerji Fiyatı = (Gelen Fatura Aktif Enerji Kalemi) / (Ana Sayaç Tüketimi)
        
        OSB kâr amacı gütmeden enerjiyi aldığı fiyattan satar
        """
        # OSB billing settings'ten paçal fiyatı al
        self.cur.execute("""
            SELECT setting_value FROM osb_billing_settings 
            WHERE setting_key = 'energy_unit_cost' 
            AND (valid_to IS NULL OR valid_to >= CURRENT_DATE)
        """)
        result = self.cur.fetchone()
        
        if result:
            return float(result['setting_value'])
        
        # Default: Tarife ortalaması
        self.cur.execute("""
            SELECT AVG((t1_rate + t2_rate + t3_rate) / 3)::numeric as avg_rate
            FROM tariffs WHERE is_active = TRUE
        """)
        result = self.cur.fetchone()
        return float(result['avg_rate'] or 2.85)
    
    def calculate_distribution_unit_price(self, year: int, voltage_level: str = 'OG') -> Tuple[float, bool]:
        """
        Dağıtım Bedeli Birim Fiyatı hesaplama
        
        Formül: Birim Dağıtım Bedeli = (Aylık İşletme Giderleri + Teknik Kayıp Maliyeti) / 
                                        (Katılımcıların Toplam Tüketimi)
        
        KRİTİK KONTROL: Hesaplanan tarife EDAŞ tarifesinden yüksekse, EDAŞ tarifesi uygulanır
        
        Returns: (rate, is_capped) - birim fiyat ve tavan uygulandı mı
        """
        # OSB dağıtım tarifesi
        self.cur.execute("""
            SELECT og_rate, ag_rate FROM osb_distribution_tariffs 
            WHERE period_year = %s AND is_active = TRUE
        """, (year,))
        osb_tariff = self.cur.fetchone()
        
        if not osb_tariff:
            # Fallback: settings tablosundan
            self.cur.execute("""
                SELECT setting_value FROM osb_billing_settings 
                WHERE setting_key = 'distribution_fee_rate'
            """)
            result = self.cur.fetchone()
            osb_rate = float(result['setting_value']) if result else 0.25
        else:
            osb_rate = float(osb_tariff['og_rate' if voltage_level == 'OG' else 'ag_rate'] or 0) / 100  # kr -> TL
        
        # EDAŞ tavan kontrolü
        self.cur.execute("""
            SELECT single_term_og_rate, single_term_ag_rate 
            FROM edas_tariffs 
            WHERE period_year = %s AND is_active = TRUE
        """, (year,))
        edas_tariff = self.cur.fetchone()
        
        is_capped = False
        if edas_tariff:
            edas_rate = float(edas_tariff['single_term_og_rate' if voltage_level == 'OG' else 'single_term_ag_rate'] or 0) / 100
            if osb_rate > edas_rate:
                osb_rate = edas_rate
                is_capped = True
        
        return osb_rate, is_capped
    
    def calculate_loss_cost(self, start_date, end_date) -> Dict:
        """
        Kayıp Elektrik Enerjisi Bedeli hesaplama
        
        Formül: Kayıp Bedeli = (Ana Sayaç - Katılımcı Toplamı) x Enerji Alış Birim Fiyatı
        """
        main_meter = self.get_main_meter_data(start_date, end_date)
        participants = self.get_all_participants_total(start_date, end_date)
        
        input_energy = main_meter['total']
        sold_energy = participants['total']
        loss_kwh = max(0, input_energy - sold_energy)
        loss_rate = (loss_kwh / input_energy * 100) if input_energy > 0 else 0
        
        energy_price = self.calculate_energy_unit_price(start_date, end_date)
        loss_cost = loss_kwh * energy_price
        
        return {
            'input_energy': round(input_energy, 3),
            'sold_energy': round(sold_energy, 3),
            'loss_kwh': round(loss_kwh, 3),
            'loss_rate': round(loss_rate, 2),
            'energy_unit_price': energy_price,
            'loss_cost': round(loss_cost, 2)
        }
    
    def calculate_revenue_requirement(self, year: int, include_loss: bool = True) -> Dict:
        """
        Dağıtım Gelir Gereksinimi (DGG) hesaplama
        
        Formül: DGG = (e + f + g + h + i + j)
        e: Geçmiş yıl yatırım giderleri
        f: Uygulama yılı yatırım giderleri
        g: İşletme giderleri
        h: Gelir düzeltme bileşeni
        i: Diğer hizmet giderleri
        j: Kayıp elektrik bedeli
        """
        cost = self.get_cost_components(year)
        if not cost:
            return None
        
        # (e) + (f): Yatırım giderleri
        investment = (float(cost['past_investment_cost'] or 0) + 
                     float(cost['current_investment_cost'] or 0))
        
        # (g): İşletme giderleri
        operating = (float(cost['personnel_cost'] or 0) + 
                    float(cost['maintenance_cost'] or 0) + 
                    float(cost['external_service_cost'] or 0))
        
        # (h): Gelir düzeltme bileşeni
        adjustment = float(cost['revenue_adjustment'] or 0)
        
        # (i): Diğer hizmet giderleri
        services = (float(cost['meter_reading_cost'] or 0) + 
                   float(cost['billing_cost'] or 0) + 
                   float(cost['customer_service_cost'] or 0))
        
        # Lisans bedelleri
        license_fees = (float(cost['license_fee'] or 0) + 
                       float(cost['annual_license_fee'] or 0))
        
        # DGG (kayıp hariç)
        dgg_without_loss = investment + operating + adjustment + services + license_fees
        
        # (j): Kayıp bedeli
        loss_cost = 0
        if include_loss:
            # Son dönem kayıp maliyeti
            loss_data = self.calculate_loss_cost(
                datetime.now().date() - timedelta(days=30),
                datetime.now().date()
            )
            loss_cost = loss_data['loss_cost']
        
        return {
            'investment_cost': round(investment, 2),
            'operating_cost': round(operating, 2),
            'adjustment': round(adjustment, 2),
            'service_cost': round(services, 2),
            'license_fees': round(license_fees, 2),
            'loss_cost': round(loss_cost, 2),
            'total_dgg': round(dgg_without_loss + loss_cost, 2),
            'dgg_without_loss': round(dgg_without_loss, 2)
        }
    
    # =========================================================================
    # FAZ 3: FATURA HESAPLAMA
    # =========================================================================
    
    def calculate_reactive_penalty(self, active: float, inductive: float, 
                                   capacitive: float, unit_price: float) -> Tuple[float, str]:
        """
        Reaktif Enerji Cezası hesaplama
        
        EPDK Kuralları:
        - (Endüktif / Aktif) > %20 ise Endüktif Ceza
        - (Kapasitif / Aktif) > %15 ise Kapasitif Ceza
        - İkisi de sınırı aşarsa sadece yüksek olan uygulanır
        """
        if active <= 0:
            return 0, None
        
        inductive_ratio = inductive / active
        capacitive_ratio = capacitive / active
        
        inductive_limit = 0.20  # %20
        capacitive_limit = 0.15  # %15
        
        inductive_penalty = 0
        capacitive_penalty = 0
        
        if inductive_ratio > inductive_limit:
            # Fazla endüktif = Endüktif - (Aktif x 0.20)
            excess_inductive = inductive - (active * inductive_limit)
            inductive_penalty = max(0, excess_inductive) * unit_price
        
        if capacitive_ratio > capacitive_limit:
            # Fazla kapasitif = Kapasitif - (Aktif x 0.15)
            excess_capacitive = capacitive - (active * capacitive_limit)
            capacitive_penalty = max(0, excess_capacitive) * unit_price
        
        # İkisi de sınırı aşarsa yüksek olan uygulanır
        if inductive_penalty > capacitive_penalty:
            return round(inductive_penalty, 2), 'inductive'
        elif capacitive_penalty > 0:
            return round(capacitive_penalty, 2), 'capacitive'
        else:
            return 0, None
    
    def calculate_osb_invoice(self, subscriber_id: int, period_id: int) -> Optional[Dict]:
        """
        OSB Fatura Hesaplama - Ana Fonksiyon
        
        Fatura Kalemleri:
        1. Aktif Enerji Bedeli (T1/T2/T3 zamanlı)
        2. Dağıtım Bedeli (OSB EPDK onaylı)
        3. Teknik Kayıp Payı (orantılı dağılım)
        4. İletim Bedeli (TEİAŞ)
        5. Reaktif Enerji Cezası (Endüktif %20 / Kapasitif %15)
        6. BTV (Belediye Tüketim Vergisi)
        7. KDV
        """
        # Dönem bilgileri
        self.cur.execute("SELECT * FROM billing_periods WHERE id = %s", (period_id,))
        period = self.cur.fetchone()
        if not period:
            return None
        
        start_date = period['period_start']
        end_date = period['period_end']
        year = start_date.year
        
        # Abone bilgileri
        self.cur.execute("""
            SELECT s.*, t.t1_rate, t.t2_rate, t.t3_rate, t.reactive_rate,
                   t.name as tariff_name, t.tariff_type
            FROM subscribers s
            JOIN tariffs t ON s.tariff_id = t.id
            WHERE s.id = %s
        """, (subscriber_id,))
        subscriber = self.cur.fetchone()
        if not subscriber:
            return None
        
        # Sayaç bilgisi
        self.cur.execute("""
            SELECT id, meter_no, multiplier FROM meters WHERE subscriber_id = %s
        """, (subscriber_id,))
        meter = self.cur.fetchone()
        if not meter:
            return None
        
        # Tüketim verisi
        consumption = self.get_participant_consumption(subscriber_id, start_date, end_date)
        
        # GES mahsuplaşma kontrolü
        solar = self.get_solar_production(subscriber_id, start_date, end_date)
        net_consumption = consumption['total'] - solar['exported'] if solar['has_solar'] else consumption['total']
        net_consumption = max(0, net_consumption)  # Negatif olamaz
        
        # Gerilim seviyesi
        voltage_level = subscriber.get('voltage_level', 'OG')
        tariff_structure = subscriber.get('tariff_structure', 'single_term')
        
        # =================================================================
        # 1. AKTİF ENERJİ BEDELİ
        # =================================================================
        t1 = consumption['t1']
        t2 = consumption['t2']
        t3 = consumption['t3']
        
        t1_rate = float(subscriber['t1_rate'])
        t2_rate = float(subscriber['t2_rate'])
        t3_rate = float(subscriber['t3_rate'])
        
        t1_amount = t1 * t1_rate
        t2_amount = t2 * t2_rate
        t3_amount = t3 * t3_rate
        energy_amount = t1_amount + t2_amount + t3_amount
        
        # =================================================================
        # 2. DAĞITIM BEDELİ
        # =================================================================
        distribution_rate, is_capped = self.calculate_distribution_unit_price(year, voltage_level)
        distribution_amount = net_consumption * distribution_rate
        
        # =================================================================
        # 3. TEKNİK KAYIP PAYI
        # =================================================================
        loss_data = self.calculate_loss_cost(start_date, end_date)
        total_sold = loss_data['sold_energy']
        total_loss = loss_data['loss_kwh']
        
        if total_sold > 0:
            loss_share_ratio = consumption['total'] / total_sold
            loss_share_kwh = total_loss * loss_share_ratio
        else:
            loss_share_ratio = 0
            loss_share_kwh = 0
        
        avg_energy_rate = (t1_rate + t2_rate + t3_rate) / 3
        technical_loss_amount = loss_share_kwh * avg_energy_rate
        
        # =================================================================
        # 4. İLETİM BEDELİ (TEİAŞ)
        # =================================================================
        self.cur.execute("""
            SELECT setting_value FROM osb_billing_settings 
            WHERE setting_key = 'transmission_fee_rate'
        """)
        result = self.cur.fetchone()
        transmission_rate = float(result['setting_value']) if result else 0.035
        transmission_amount = net_consumption * transmission_rate
        
        # =================================================================
        # 5. REAKTİF ENERJİ CEZASI
        # =================================================================
        reactive_rate = float(subscriber['reactive_rate'])
        reactive_amount, reactive_type = self.calculate_reactive_penalty(
            consumption['total'],
            consumption['inductive'],
            consumption['capacitive'],
            reactive_rate
        )
        
        # =================================================================
        # 6. GÜÇ BEDELİ (Çift Terimli Tarife)
        # =================================================================
        capacity_amount = 0
        capacity_excess_amount = 0
        if tariff_structure == 'dual_term':
            contract_demand = float(subscriber.get('contract_demand', 0))
            max_demand = consumption['max_demand']
            
            self.cur.execute("""
                SELECT capacity_rate, capacity_excess_rate 
                FROM osb_distribution_tariffs 
                WHERE period_year = %s AND tariff_type = 'dual_term' AND is_active = TRUE
            """, (year,))
            dual_tariff = self.cur.fetchone()
            
            if dual_tariff and contract_demand > 0:
                capacity_rate = float(dual_tariff['capacity_rate'] or 0) / 100  # kr -> TL
                capacity_amount = contract_demand * capacity_rate
                
                # Güç aşımı kontrolü
                if max_demand > contract_demand:
                    excess_demand = max_demand - contract_demand
                    excess_rate = float(dual_tariff['capacity_excess_rate'] or 0) / 100
                    if excess_rate == 0:
                        excess_rate = capacity_rate * 2  # Max 2 kat
                    capacity_excess_amount = excess_demand * excess_rate
        
        # =================================================================
        # ARA TOPLAM
        # =================================================================
        subtotal = (energy_amount + distribution_amount + technical_loss_amount + 
                   transmission_amount + reactive_amount + capacity_amount + 
                   capacity_excess_amount)
        
        # GES kredisi (varsa)
        solar_credit = 0
        if solar['has_solar'] and solar['exported'] > 0:
            # Şebekeye verilen enerji için alış fiyatı üzerinden kredi
            solar_credit = solar['exported'] * avg_energy_rate * 0.8  # %80 geri alım
            subtotal -= solar_credit
        
        # =================================================================
        # 7. BTV (Belediye Tüketim Vergisi)
        # =================================================================
        self.cur.execute("""
            SELECT setting_value FROM osb_billing_settings 
            WHERE setting_key = 'btv_rate'
        """)
        result = self.cur.fetchone()
        btv_rate = float(result['setting_value']) if result else 0.05
        btv_amount = subtotal * btv_rate
        
        # =================================================================
        # 8. KDV
        # =================================================================
        self.cur.execute("""
            SELECT setting_value FROM osb_billing_settings 
            WHERE setting_key = 'kdv_rate'
        """)
        result = self.cur.fetchone()
        kdv_rate = float(result['setting_value']) if result else 0.20
        kdv_amount = (subtotal + btv_amount) * kdv_rate
        
        # =================================================================
        # GENEL TOPLAM
        # =================================================================
        total_amount = subtotal + btv_amount + kdv_amount
        
        return {
            'subscriber': dict(subscriber),
            'period': dict(period),
            'meter_id': meter['id'],
            'meter_no': meter['meter_no'],
            'multiplier': float(meter['multiplier'] or 1),
            
            # Tüketim
            'consumption': {
                't1': round(t1, 3),
                't2': round(t2, 3),
                't3': round(t3, 3),
                'total': round(consumption['total'], 3),
                'inductive': round(consumption['inductive'], 3),
                'capacitive': round(consumption['capacitive'], 3),
                'max_demand': round(consumption['max_demand'], 3)
            },
            
            # GES
            'solar': solar,
            'net_consumption': round(net_consumption, 3),
            
            # Aktif enerji
            't1_rate': t1_rate,
            't2_rate': t2_rate,
            't3_rate': t3_rate,
            't1_amount': round(t1_amount, 2),
            't2_amount': round(t2_amount, 2),
            't3_amount': round(t3_amount, 2),
            'energy_amount': round(energy_amount, 2),
            
            # Dağıtım
            'voltage_level': voltage_level,
            'distribution_rate': distribution_rate,
            'distribution_capped': is_capped,
            'distribution_amount': round(distribution_amount, 2),
            
            # Teknik kayıp
            'technical_loss_share_ratio': round(loss_share_ratio, 4),
            'technical_loss_share': round(loss_share_kwh, 3),
            'technical_loss_amount': round(technical_loss_amount, 2),
            
            # İletim
            'transmission_rate': transmission_rate,
            'transmission_amount': round(transmission_amount, 2),
            
            # Reaktif
            'reactive_rate': reactive_rate,
            'reactive_type': reactive_type,
            'reactive_amount': round(reactive_amount, 2),
            
            # Güç bedeli (çift terimli)
            'tariff_structure': tariff_structure,
            'capacity_amount': round(capacity_amount, 2),
            'capacity_excess_amount': round(capacity_excess_amount, 2),
            
            # GES kredi
            'solar_credit_amount': round(solar_credit, 2),
            
            # Vergiler
            'subtotal': round(subtotal, 2),
            'btv_rate': btv_rate,
            'btv_amount': round(btv_amount, 2),
            'kdv_rate': kdv_rate,
            'kdv_amount': round(kdv_amount, 2),
            'total_amount': round(total_amount, 2),
            
            # Ek bilgiler
            'loss_info': {
                'input': loss_data['input_energy'],
                'sold': loss_data['sold_energy'],
                'loss': loss_data['loss_kwh'],
                'loss_rate': loss_data['loss_rate']
            }
        }
    
    # =========================================================================
    # FAZ 4: FATURA KAYIT VE RAPORLAMA
    # =========================================================================
    
    def create_invoice(self, subscriber_id: int, period_id: int, tariff_id: int) -> Dict:
        """
        Fatura oluştur ve veritabanına kaydet
        """
        invoice_data = self.calculate_osb_invoice(subscriber_id, period_id)
        if not invoice_data:
            return {'success': False, 'error': 'Fatura hesaplanamadı'}
        
        try:
            # Fatura numarası
            self.cur.execute(
                "SELECT COUNT(*) as count FROM invoices WHERE period_id = %s", 
                (period_id,)
            )
            count = self.cur.fetchone()['count']
            period_name = invoice_data['period']['name'].replace(' ', '')
            invoice_no = f"FTR-{period_name}-{count + 1:05d}"
            
            # Fatura kaydı
            self.cur.execute("""
                INSERT INTO invoices (
                    invoice_no, subscriber_id, meter_id, period_id, tariff_id,
                    t1_consumption, t2_consumption, t3_consumption, total_consumption,
                    inductive_reactive, capacitive_reactive,
                    t1_amount, t2_amount, t3_amount, reactive_amount,
                    distribution_amount, technical_loss_share, technical_loss_amount,
                    transmission_amount, btv_amount,
                    capacity_amount, capacity_excess_amount,
                    solar_production_kwh, solar_credit_amount, net_consumption,
                    voltage_level, tariff_structure,
                    subtotal, vat_rate, vat_amount, total_amount,
                    status, issue_date, due_date
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    'issued', %s, %s
                ) RETURNING id
            """, (
                invoice_no, subscriber_id, invoice_data['meter_id'], period_id, tariff_id,
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
                invoice_data['capacity_amount'],
                invoice_data['capacity_excess_amount'],
                invoice_data['solar']['production'] if invoice_data['solar']['has_solar'] else None,
                invoice_data['solar_credit_amount'],
                invoice_data['net_consumption'],
                invoice_data['voltage_level'],
                invoice_data['tariff_structure'],
                invoice_data['subtotal'],
                invoice_data['kdv_rate'] * 100,
                invoice_data['kdv_amount'],
                invoice_data['total_amount'],
                invoice_data['period']['invoice_date'],
                invoice_data['period']['due_date']
            ))
            
            invoice_id = self.cur.fetchone()['id']
            self.conn.commit()
            
            # Fatura kalemleri
            items = [
                ('energy', 'T1 - Gündüz Tüketimi (06:00-17:00)', 
                 invoice_data['consumption']['t1'], invoice_data['t1_rate'], invoice_data['t1_amount']),
                ('energy', 'T2 - Puant Tüketimi (17:00-22:00)', 
                 invoice_data['consumption']['t2'], invoice_data['t2_rate'], invoice_data['t2_amount']),
                ('energy', 'T3 - Gece Tüketimi (22:00-06:00)', 
                 invoice_data['consumption']['t3'], invoice_data['t3_rate'], invoice_data['t3_amount']),
                ('distribution', 'OSB Dağıtım Bedeli', 
                 invoice_data['net_consumption'], invoice_data['distribution_rate'], 
                 invoice_data['distribution_amount']),
                ('technical_loss', 'Teknik Kayıp Payı', 
                 invoice_data['technical_loss_share'], 0, invoice_data['technical_loss_amount']),
                ('transmission', 'TEİAŞ İletim Bedeli', 
                 invoice_data['net_consumption'], invoice_data['transmission_rate'], 
                 invoice_data['transmission_amount']),
            ]
            
            if invoice_data['reactive_amount'] > 0:
                reactive_desc = f"Reaktif Enerji Cezası ({'Endüktif' if invoice_data['reactive_type'] == 'inductive' else 'Kapasitif'})"
                items.append(('reactive', reactive_desc,
                             invoice_data['consumption']['inductive'] + invoice_data['consumption']['capacitive'],
                             invoice_data['reactive_rate'], invoice_data['reactive_amount']))
            
            if invoice_data['capacity_amount'] > 0:
                items.append(('capacity', 'Güç Bedeli (Sözleşme Gücü)',
                             invoice_data['subscriber'].get('contract_demand', 0), 0,
                             invoice_data['capacity_amount']))
            
            if invoice_data['capacity_excess_amount'] > 0:
                items.append(('capacity_excess', 'Güç Aşım Bedeli',
                             invoice_data['consumption']['max_demand'], 0,
                             invoice_data['capacity_excess_amount']))
            
            if invoice_data['solar_credit_amount'] > 0:
                items.append(('solar_credit', 'GES Üretim Kredisi',
                             invoice_data['solar']['exported'], 0,
                             -invoice_data['solar_credit_amount']))
            
            for item_type, desc, qty, price, amount in items:
                if amount and float(amount) != 0:
                    self.cur.execute("""
                        INSERT INTO invoice_items 
                        (invoice_id, item_type, description, quantity, unit_price, total_amount)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (invoice_id, item_type, desc, qty, price, amount))
            
            self.conn.commit()
            
            return {
                'success': True,
                'invoice_id': invoice_id,
                'invoice_no': invoice_no,
                'total_amount': invoice_data['total_amount']
            }
            
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_invoice_preview(self, subscriber_id: int, period_id: int) -> Optional[Dict]:
        """
        Fatura önizleme (kaydetmeden hesapla)
        """
        return self.calculate_osb_invoice(subscriber_id, period_id)
    
    def get_revenue_adjustment(self, year: int) -> Dict:
        """
        Gelir Düzeltme Bileşeni hesaplama
        
        Öngörülen gelir vs gerçekleşen gelir farkı
        Bir sonraki yılın DGG'sine eklenir/çıkarılır
        """
        # Öngörülen gelir (DGG)
        dgg = self.calculate_revenue_requirement(year, include_loss=True)
        if not dgg:
            return {'error': 'Maliyet bileşenleri bulunamadı'}
        
        projected_revenue = dgg['total_dgg']
        
        # Gerçekleşen gelir (faturalanan toplam dağıtım bedeli)
        self.cur.execute("""
            SELECT COALESCE(SUM(distribution_amount), 0)::numeric as actual
            FROM invoices i
            JOIN billing_periods bp ON i.period_id = bp.id
            WHERE EXTRACT(YEAR FROM bp.period_start) = %s
            AND i.status != 'cancelled'
        """, (year,))
        actual_revenue = float(self.cur.fetchone()['actual'] or 0)
        
        # Fark
        adjustment = actual_revenue - projected_revenue
        
        return {
            'year': year,
            'projected_revenue': round(projected_revenue, 2),
            'actual_revenue': round(actual_revenue, 2),
            'adjustment': round(adjustment, 2),
            'adjustment_type': 'surplus' if adjustment > 0 else 'deficit',
            'next_year_impact': -adjustment  # Fazla toplandıysa düşülür, eksik kaldıysa eklenir
        }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_osb_billing_service():
    """OSB Billing Service factory"""
    return OSBBillingService()

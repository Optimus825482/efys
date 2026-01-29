"""
Test OSB Billing - EPDK Uyumlu Fatura Hesaplama
"""
from services.database_extensions import preview_invoice
from services.database import DatabaseService

def test_preview():
    db = DatabaseService()
    try:
        # Mevcut abone al
        db.cur.execute("SELECT id, subscriber_code, name FROM subscribers LIMIT 1")
        sub = db.cur.fetchone()
        
        # Mevcut dönem al
        db.cur.execute("SELECT id, name FROM billing_periods ORDER BY period_start DESC LIMIT 1")
        period = db.cur.fetchone()
        
        if not sub or not period:
            print("Veri bulunamadı!")
            return
        
        print(f"Abone: {sub['subscriber_code']} - {sub['name']}")
        print(f"Dönem: {period['name']}")
        print("-" * 50)
        
        invoice = preview_invoice(sub['id'], period['id'])
        
        if not invoice:
            print("Fatura hesaplanamadı!")
            return
        
        print("FATURA ÖNİZLEME BAŞARILI!")
        print("-" * 50)
        print(f"Tüketim:")
        print(f"  T1 (Gündüz): {invoice['consumption']['t1']:,.0f} kWh")
        print(f"  T2 (Puant):  {invoice['consumption']['t2']:,.0f} kWh")
        print(f"  T3 (Gece):   {invoice['consumption']['t3']:,.0f} kWh")
        print(f"  TOPLAM:      {invoice['consumption']['total']:,.0f} kWh")
        print("-" * 50)
        print(f"Fatura Kalemleri:")
        print(f"  Aktif Enerji:    TL{invoice['energy_amount']:,.2f}")
        print(f"  Dağıtım:         TL{invoice['distribution_amount']:,.2f} {'(EDAŞ Tavan)' if invoice.get('distribution_capped') else ''}")
        print(f"  Teknik Kayıp:    TL{invoice['technical_loss_amount']:,.2f}")
        print(f"  İletim (TEİAŞ):  TL{invoice['transmission_amount']:,.2f}")
        print(f"  Reaktif Ceza:    TL{invoice['reactive_amount']:,.2f}")
        print(f"  Güç Bedeli:      TL{invoice.get('capacity_amount', 0):,.2f}")
        if invoice.get('solar', {}).get('has_solar'):
            print(f"  GES Kredi:       -TL{invoice.get('solar_credit_amount', 0):,.2f}")
        print("-" * 50)
        print(f"  Ara Toplam:      TL{invoice['subtotal']:,.2f}")
        print(f"  BTV (%{invoice['btv_rate']*100:.0f}):       TL{invoice['btv_amount']:,.2f}")
        print(f"  KDV (%{invoice['kdv_rate']*100:.0f}):       TL{invoice['kdv_amount']:,.2f}")
        print("=" * 50)
        print(f"  GENEL TOPLAM:    TL{invoice['total_amount']:,.2f}")
        print("=" * 50)
        
    finally:
        db.close()

if __name__ == "__main__":
    test_preview()

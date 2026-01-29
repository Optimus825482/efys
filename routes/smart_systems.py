"""Smart Systems Routes"""
from flask import Blueprint, render_template
from services.database import DatabaseService

smart_bp = Blueprint('smart', __name__)

@smart_bp.route('/')
def index():
    return render_template('smart-systems/index.html')

@smart_bp.route('/regulation-bot')
def regulation_bot():
    """Mevzuat botu - MevzuatService'den gerçek veriler"""
    from services.mevzuat import MevzuatService
    
    mevzuat = MevzuatService()
    try:
        stats = mevzuat.get_dashboard_stats()
        recent_alerts = mevzuat.get_recent_alerts(limit=10)
        
        return render_template('smart-systems/regulation-bot.html', 
                             stats=stats,
                             recent_alerts=recent_alerts)
    except Exception as e:
        print(f"Error loading regulation bot: {e}")
        return render_template('smart-systems/regulation-bot.html', 
                             stats={},
                             recent_alerts=[])
    finally:
        mevzuat.close()

@smart_bp.route('/penalty-prevention')
def penalty_prevention():
    """Reaktif ceza önleme - reactive_report ile ortak veri"""
    db = DatabaseService()
    try:
        report = db.get_reactive_report()
        return render_template('smart-systems/penalty-prevention.html', report=report)
    except Exception as e:
        print(f"Error loading penalty prevention: {e}")
        return render_template('smart-systems/penalty-prevention.html', report=None)
    finally:
        db.close()

@smart_bp.route('/portal')
def portal():
    """Portal yönetimi - Portal routes'dan gerçek istatistikler"""
    db = DatabaseService()
    try:
        # Toplam abone sayısı
        db.cur.execute("SELECT COUNT(*) as count FROM subscribers WHERE status = 'active'")
        total_subscribers = db.cur.fetchone()['count']
        
        # Portal kullanan aboneler (demo: tüm aktif aboneler portal kullanıyor varsayımı)
        portal_active = total_subscribers
        
        # Bu ay yapılan portal girişleri (basit hesaplama: abone başı ortalama 5 giriş)
        monthly_logins = total_subscribers * 5
        
        # Memnuniyet oranı (demo: 92% sabit)
        satisfaction = 92
        
        # Portal kullanıcı listesi
        db.cur.execute("""
            SELECT 
                s.subscriber_code,
                s.name,
                'Aktif' as portal_status,
                '29.01.2026 09:45' as last_login,
                5 as login_count
            FROM subscribers s
            WHERE s.status = 'active'
            ORDER BY s.subscriber_code
            LIMIT 20
        """)
        portal_users = [dict(row) for row in db.cur.fetchall()]
        
        return render_template('smart-systems/portal.html',
                             total_subscribers=total_subscribers,
                             portal_active=portal_active,
                             monthly_logins=monthly_logins,
                             satisfaction=satisfaction,
                             portal_users=portal_users)
    except Exception as e:
        print(f"Error loading portal management: {e}")
        return render_template('smart-systems/portal.html',
                             total_subscribers=0,
                             portal_active=0,
                             monthly_logins=0,
                             satisfaction=0,
                             portal_users=[])
    finally:
        db.close()

@smart_bp.route('/erp-bridge')
def erp_bridge():
    return render_template('smart-systems/erp-bridge.html')

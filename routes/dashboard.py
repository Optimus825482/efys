"""Dashboard Routes - PostgreSQL Entegrasyonu"""
from flask import Blueprint, render_template, jsonify, request
from services.database import (
    get_dashboard_stats,
    get_daily_consumption_chart,
    get_reactive_status,
    get_top_consumers
)
from services.mevzuat import MevzuatService

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def login():
    """Login/Landing page - Demo mode with OSB and Sanayici buttons"""
    return render_template('login.html')


@dashboard_bp.route('/dashboard')
def index():
    """Main dashboard page with real data"""
    try:
        # Gerçek veritabanı verileri
        stats = get_dashboard_stats()
        chart_data = get_daily_consumption_chart(7)
        reactive = get_reactive_status()
        top_consumers = get_top_consumers(5)
        
        # KPI kartları için formatlama - Gerçek metrikler
        kpis = {
            'total_subscribers': {
                'value': str(stats['total_subscribers']),
                'unit': 'abone',
                'change': f"{stats['active_subscribers']} aktif"
            },
            'monthly_consumption': {
                'value': f"{stats['monthly_consumption']:,}".replace(',', '.'),
                'unit': 'kWh',
                'change': f"{stats['reading_count']:,} okuma".replace(',', '.')
            },
            'total_readings': {
                'value': f"{stats['reading_count']:,}".replace(',', '.'),
                'unit': 'okuma',
                'change': f"Bu ay"
            },
            'active_meters': {
                'value': str(stats['active_meters']),
                'unit': 'sayaç',
                'change': f"{stats['total_meters']} toplam"
            }
        }
        
        # Son alarmlar (demo)
        alarms = [
            {'type': 'info', 'message': f"Toplam {stats['total_subscribers']} abone aktif", 'time': 'Şimdi'},
            {'type': 'success', 'message': f"Bu ay {stats['monthly_consumption']:,} kWh tüketim".replace(',', '.'), 'time': '5 dk önce'},
            {'type': 'warning', 'message': f"Ortalama güç faktörü: {reactive['ortalama_cos_phi']:.3f}", 'time': '10 dk önce'},
        ]
        
        # Mevzuat uyarıları
        mevzuat_data = None
        try:
            mevzuat_svc = MevzuatService()
            mevzuat_data = {
                'stats': mevzuat_svc.get_dashboard_stats(),
                'recent': mevzuat_svc.get_recent_alerts(limit=3)
            }
            mevzuat_svc.close()
        except Exception as me:
            print(f"Mevzuat widget error: {me}")
        
        return render_template('dashboard/index.html', 
                             kpis=kpis, 
                             alarms=alarms,
                             chart_data=chart_data,
                             reactive=reactive,
                             top_consumers=top_consumers,
                             mevzuat=mevzuat_data)
    except Exception as e:
        # Hata durumunda demo veri
        print(f"Dashboard error: {e}")
        kpis = {
            'total_consumption': {'value': '0', 'unit': 'kWh', 'change': 'DB Hatası'},
            'active_subscribers': {'value': '0', 'unit': 'abone', 'change': ''},
            'unpaid_invoices': {'value': '₺0', 'unit': '', 'change': ''},
            'reactive_penalty': {'value': '₺0', 'unit': '', 'change': ''}
        }
        return render_template('dashboard/index.html', kpis=kpis, alarms=[])


@dashboard_bp.route('/api/chart/daily')
def api_daily_chart():
    """API: Günlük tüketim grafiği verisi"""
    try:
        data = get_daily_consumption_chart(7)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/chart/hourly')
def api_hourly_chart():
    """API: Saatlik tüketim profili"""
    from services.database import get_hourly_consumption_profile
    try:
        data = get_hourly_consumption_profile()
        return jsonify({
            'labels': [f"{r['saat']:02d}:00" for r in data],
            'values': [r['tuketim'] for r in data]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/stats')
def api_stats():
    """API: Dashboard istatistikleri"""
    try:
        stats = get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/live')
def live_monitoring():
    """Live monitoring page"""
    from services.database import DatabaseService
    db = DatabaseService()
    try:
        # Anlık okuma verileri
        readings = db.get_instant_readings(limit=20)
        stats = db.get_meter_stats()
        
        return render_template('dashboard/live-monitoring.html', 
                             readings=readings,
                             stats=stats)
    except Exception as e:
        print(f"Error loading live monitoring: {e}")
        return render_template('dashboard/live-monitoring.html', readings=[], stats=None)
    finally:
        db.close()

@dashboard_bp.route('/reactive')
def reactive_radar():
    """Reactive energy radar"""
    reactive = get_reactive_status()
    return render_template('dashboard/reactive-radar.html', reactive=reactive)

@dashboard_bp.route('/alarms')
def alarm_center():
    """Alarm center"""
    from services import get_alarms
    try:
        alarms = get_alarms(limit=50)
        
        # Alarm istatistikleri
        stats = {
            'total': len(alarms),
            'critical': len([a for a in alarms if a.get('severity') == 'critical']),
            'warning': len([a for a in alarms if a.get('severity') == 'warning']),
            'info': len([a for a in alarms if a.get('severity') == 'info']),
            'unacknowledged': len([a for a in alarms if not a.get('acknowledged')])
        }
        
        return render_template('dashboard/alarm-center.html', alarms=alarms, stats=stats)
    except Exception as e:
        print(f"Error loading alarm center: {e}")
        return render_template('dashboard/alarm-center.html', alarms=[], stats=None)

@dashboard_bp.route('/api/reactive/trend')
def api_reactive_trend():
    """API: Reaktif enerji trendi (günülük)"""
    from services.database import DatabaseService
    db = DatabaseService()
    try:
        days = request.args.get('days', 30, type=int)
        
        db.cur.execute("""
            SELECT 
                DATE(reading_time) as tarih,
                AVG(power_factor)::numeric(5,3) as avg_pf,
                SUM(inductive_reactive)::int as inductive,
                SUM(capacitive_reactive)::int as capacitive
            FROM readings
            WHERE reading_time >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY DATE(reading_time)
            ORDER BY tarih
        """, (days,))
        data = [dict(row) for row in db.cur.fetchall()]
        
        return jsonify({
            'success': True,
            'data': {
                'labels': [str(d['tarih']) for d in data],
                'avg_pf': [float(d['avg_pf']) for d in data],
                'inductive': [d['inductive'] for d in data],
                'capacitive': [d['capacitive'] for d in data]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        db.close()


# =============================================================================
# API ENDPOINTS
# =============================================================================

@dashboard_bp.route('/api/alarms')
def api_alarms():
    """API: Alarm listesi"""
    from services import get_alarms
    try:
        limit = request.args.get('limit', 50, type=int)
        alarms = get_alarms(limit=limit)
        
        return jsonify({
            'success': True,
            'data': alarms
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/api/alarms/acknowledge/<int:alarm_id>', methods=['POST'])
def api_acknowledge_alarm(alarm_id):
    """API: Alarm onaylama"""
    from services import acknowledge_alarm
    try:
        result = acknowledge_alarm(alarm_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Alarm onaylandı'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

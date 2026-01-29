"""Settings Routes"""
from flask import Blueprint, render_template, jsonify, request
from services.mevzuat import MevzuatService
from services.database import DatabaseService

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/')
def index():
    return render_template('settings/index.html')

@settings_bp.route('/users')
def users():
    return render_template('settings/users.html')

@settings_bp.route('/roles')
def roles():
    return render_template('settings/roles.html')

@settings_bp.route('/parameters')
def parameters():
    """Sistem parametreleri"""
    db = DatabaseService()
    try:
        # OSB faturalama ayarlarını al
        db.cur.execute("""
            SELECT setting_key, setting_value 
            FROM osb_billing_settings 
            WHERE valid_to IS NULL OR valid_to >= CURRENT_DATE
        """)
        params = {row['setting_key']: row['setting_value'] for row in db.cur.fetchall()}
        return render_template('settings/parameters.html', params=params)
    except Exception as e:
        print(f"Error loading parameters: {e}")
        return render_template('settings/parameters.html', params={})
    finally:
        db.close()

@settings_bp.route('/email-sms')
def email_sms():
    """Email/SMS ayarları"""
    db = DatabaseService()
    try:
        # Ayarları veritabanından çek (varsa)
        settings = {}
        try:
            db.cur.execute("""
                SELECT setting_key, setting_value 
                FROM osb_billing_settings 
                WHERE setting_key LIKE 'smtp_%' OR setting_key LIKE 'sms_%'
            """)
            settings = {row['setting_key']: row['setting_value'] for row in db.cur.fetchall()}
        except:
            pass
        return render_template('settings/email-sms.html', settings=settings)
    except Exception as e:
        print(f"Error loading email-sms settings: {e}")
        return render_template('settings/email-sms.html', settings={})
    finally:
        db.close()

@settings_bp.route('/backup')
def backup():
    return render_template('settings/backup.html')

@settings_bp.route('/logs')
def logs():
    """Sistem logları"""
    db = DatabaseService()
    try:
        # Son 100 log kaydı
        db.cur.execute("""
            SELECT id, log_level, module, message, created_at
            FROM system_logs
            ORDER BY created_at DESC
            LIMIT 100
        """)
        logs = [dict(row) for row in db.cur.fetchall()]
        return render_template('settings/logs.html', logs=logs)
    except Exception as e:
        print(f"Error loading logs: {e}")
        # Tablo yoksa veya hata varsa boş liste döndür
        return render_template('settings/logs.html', logs=[])
    finally:
        db.close()

@settings_bp.route('/security')
def security():
    return render_template('settings/security.html')


# ==================== MEVZUAT TAKİP ====================

@settings_bp.route('/mevzuat')
def mevzuat():
    """Mevzuat takip sayfası"""
    svc = MevzuatService()
    try:
        sources = svc.get_all_sources()
        keywords = svc.get_all_keywords()
        alerts = svc.get_alerts(limit=50)
        stats = svc.get_dashboard_stats()
        return render_template('settings/mevzuat.html',
                             sources=sources,
                             keywords=keywords,
                             alerts=alerts,
                             stats=stats)
    finally:
        svc.close()


# -------------------- Sources API --------------------

@settings_bp.route('/api/mevzuat/sources', methods=['GET'])
def api_get_sources():
    """Get all mevzuat sources"""
    svc = MevzuatService()
    try:
        sources = svc.get_all_sources()
        return jsonify({'success': True, 'data': sources})
    finally:
        svc.close()


@settings_bp.route('/api/mevzuat/sources', methods=['POST'])
def api_add_source():
    """Add a new source"""
    svc = MevzuatService()
    try:
        data = request.get_json()
        source = svc.add_source(
            name=data['name'],
            url=data['url'],
            source_type=data.get('source_type', 'web'),
            check_interval_hours=data.get('check_interval_hours', 24)
        )
        return jsonify({'success': True, 'data': source})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        svc.close()


@settings_bp.route('/api/mevzuat/sources/<int:source_id>', methods=['PUT'])
def api_update_source(source_id):
    """Update a source"""
    svc = MevzuatService()
    try:
        data = request.get_json()
        success = svc.update_source(source_id, **data)
        return jsonify({'success': success})
    finally:
        svc.close()


@settings_bp.route('/api/mevzuat/sources/<int:source_id>', methods=['DELETE'])
def api_delete_source(source_id):
    """Delete a source"""
    svc = MevzuatService()
    try:
        success = svc.delete_source(source_id)
        return jsonify({'success': success})
    finally:
        svc.close()


# -------------------- Keywords API --------------------

@settings_bp.route('/api/mevzuat/keywords', methods=['GET'])
def api_get_keywords():
    """Get all keywords"""
    svc = MevzuatService()
    try:
        keywords = svc.get_all_keywords()
        return jsonify({'success': True, 'data': keywords})
    finally:
        svc.close()


@settings_bp.route('/api/mevzuat/keywords', methods=['POST'])
def api_add_keyword():
    """Add a new keyword"""
    svc = MevzuatService()
    try:
        data = request.get_json()
        keyword = svc.add_keyword(
            keyword=data['keyword'],
            priority=data.get('priority', 1)
        )
        return jsonify({'success': True, 'data': keyword})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        svc.close()


@settings_bp.route('/api/mevzuat/keywords/<int:keyword_id>', methods=['PUT'])
def api_update_keyword(keyword_id):
    """Update a keyword"""
    svc = MevzuatService()
    try:
        data = request.get_json()
        success = svc.update_keyword(keyword_id, **data)
        return jsonify({'success': success})
    finally:
        svc.close()


@settings_bp.route('/api/mevzuat/keywords/<int:keyword_id>', methods=['DELETE'])
def api_delete_keyword(keyword_id):
    """Delete a keyword"""
    svc = MevzuatService()
    try:
        success = svc.delete_keyword(keyword_id)
        return jsonify({'success': success})
    finally:
        svc.close()


# -------------------- Alerts API --------------------

@settings_bp.route('/api/mevzuat/alerts', methods=['GET'])
def api_get_alerts():
    """Get alerts with optional filters"""
    svc = MevzuatService()
    try:
        unread_only = request.args.get('unread', 'false').lower() == 'true'
        important_only = request.args.get('important', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 50))
        
        alerts = svc.get_alerts(limit=limit, unread_only=unread_only,
                               important_only=important_only)
        return jsonify({'success': True, 'data': alerts})
    finally:
        svc.close()


@settings_bp.route('/api/mevzuat/alerts/<int:alert_id>/read', methods=['POST'])
def api_mark_alert_read(alert_id):
    """Mark an alert as read"""
    svc = MevzuatService()
    try:
        success = svc.mark_alert_read(alert_id)
        return jsonify({'success': success})
    finally:
        svc.close()


@settings_bp.route('/api/mevzuat/alerts/read-all', methods=['POST'])
def api_mark_all_read():
    """Mark all alerts as read"""
    svc = MevzuatService()
    try:
        count = svc.mark_all_read()
        return jsonify({'success': True, 'count': count})
    finally:
        svc.close()


@settings_bp.route('/api/mevzuat/alerts/<int:alert_id>/important', methods=['POST'])
def api_toggle_important(alert_id):
    """Toggle important status"""
    svc = MevzuatService()
    try:
        success = svc.toggle_important(alert_id)
        return jsonify({'success': success})
    finally:
        svc.close()


@settings_bp.route('/api/mevzuat/alerts/<int:alert_id>', methods=['DELETE'])
def api_delete_alert(alert_id):
    """Delete an alert"""
    svc = MevzuatService()
    try:
        success = svc.delete_alert(alert_id)
        return jsonify({'success': success})
    finally:
        svc.close()


# -------------------- Scan API --------------------

@settings_bp.route('/api/mevzuat/scan', methods=['POST'])
def api_scan_sources():
    """Scan all sources for new content"""
    svc = MevzuatService()
    try:
        results = svc.scan_all_sources()
        return jsonify({'success': True, 'data': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        svc.close()


@settings_bp.route('/api/mevzuat/stats', methods=['GET'])
def api_get_stats():
    """Get dashboard stats"""
    svc = MevzuatService()
    try:
        stats = svc.get_dashboard_stats()
        recent = svc.get_recent_alerts(limit=5)
        return jsonify({'success': True, 'data': {'stats': stats, 'recent': recent}})
    finally:
        svc.close()

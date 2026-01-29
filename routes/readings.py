"""Readings Routes - PostgreSQL Integrated"""
from flask import Blueprint, render_template, request, jsonify, flash
from services.database import DatabaseService
from services import (
    create_scheduled_reading,
    get_scheduled_readings,
    execute_scheduled_reading,
    retry_failed_reading,
    get_failed_readings,
    bulk_start_readings
)

readings_bp = Blueprint('readings', __name__)

@readings_bp.route('/')
def index():
    """Okuma işlemleri ana sayfası"""
    db = DatabaseService()
    try:
        stats = db.get_reading_stats()
        return render_template('readings/index.html', stats=stats)
    except Exception as e:
        print(f"Error loading readings index: {e}")
        return render_template('readings/index.html', stats=None)
    finally:
        db.close()

@readings_bp.route('/instant')
def instant():
    """Anlık okuma sayfası"""
    db = DatabaseService()
    try:
        readings = db.get_instant_readings()
        stats = db.get_reading_stats()
        return render_template('readings/instant.html', 
                             readings=readings, 
                             stats=stats)
    except Exception as e:
        print(f"Error loading instant readings: {e}")
        return render_template('readings/instant.html', readings=[], stats=None)
    finally:
        db.close()

@readings_bp.route('/scheduled')
def scheduled():
    """Zamanlanmış okumalar sayfası"""
    try:
        scheduled_readings = get_scheduled_readings()
        return render_template('readings/scheduled.html', readings=scheduled_readings)
    except Exception as e:
        print(f"Error loading scheduled readings: {e}")
        return render_template('readings/scheduled.html', readings=[])

@readings_bp.route('/bulk')
def bulk():
    """Toplu okuma sayfası"""
    db = DatabaseService()
    try:
        meters = db.get_all_meters()
        stats = db.get_meter_stats()
        return render_template('readings/bulk.html', meters=meters, stats=stats)
    except Exception as e:
        print(f"Error loading bulk readings: {e}")
        return render_template('readings/bulk.html', meters=[], stats=None)
    finally:
        db.close()

@readings_bp.route('/history')
def history():
    """Okuma geçmişi sayfası"""
    db = DatabaseService()
    try:
        data = db.get_readings_with_stats(limit=50)
        trend = db.get_daily_reading_trend(days=7)
        return render_template('readings/history.html', 
                             readings=data['readings'],
                             stats=data['stats'],
                             trend=trend)
    except Exception as e:
        print(f"Error loading reading history: {e}")
        return render_template('readings/history.html', readings=[], stats=None, trend=[])
    finally:
        db.close()

@readings_bp.route('/failed')
def failed():
    """Başarısız okumalar sayfası"""
    try:
        failed_readings = get_failed_readings()
        return render_template('readings/failed.html', readings=failed_readings)
    except Exception as e:
        print(f"Error loading failed readings: {e}")
        return render_template('readings/failed.html', readings=[])

# =============================================================================
# API ENDPOINTS
# =============================================================================

@readings_bp.route('/api/instant')
def api_instant():
    """API: Anlık okuma verileri"""
    db = DatabaseService()
    try:
        readings = db.get_instant_readings(limit=50)
        return jsonify({
            'success': True,
            'data': readings
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@readings_bp.route('/api/schedule', methods=['POST'])
def api_schedule_reading():
    """API: Okuma zamanla"""
    try:
        data = request.get_json()
        meter_id = data.get('meter_id')
        scheduled_time = data.get('scheduled_time')
        
        if not all([meter_id, scheduled_time]):
            return jsonify({
                'success': False,
                'error': 'meter_id ve scheduled_time gerekli'
            }), 400
        
        result = create_scheduled_reading(meter_id, scheduled_time)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Okuma zamanlandı'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@readings_bp.route('/api/retry/<int:reading_id>', methods=['POST'])
def api_retry_reading(reading_id):
    """API: Başarısız okumayı tekrar dene"""
    try:
        result = retry_failed_reading(reading_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Okuma yeniden deneniyor'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@readings_bp.route('/api/bulk-start', methods=['POST'])
def api_bulk_start():
    """API: Toplu okuma başlat"""
    try:
        data = request.get_json()
        meter_ids = data.get('meter_ids', [])
        
        if not meter_ids:
            return jsonify({
                'success': False,
                'error': 'meter_ids listesi gerekli'
            }), 400
        
        result = bulk_start_readings(meter_ids)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': f"{result['started']} okuma başlatıldı"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@readings_bp.route('/api/execute/<int:scheduled_id>', methods=['POST'])
def api_execute_scheduled(scheduled_id):
    """API: Zamanlanmış okumayı çalıştır"""
    try:
        result = execute_scheduled_reading(scheduled_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Okuma çalıştırıldı'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@readings_bp.route('/api/stats')
def api_stats():
    """API: Okuma istatistikleri"""
    db = DatabaseService()
    try:
        stats = db.get_reading_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@readings_bp.route('/api/trend/<int:days>')
def api_trend(days=7):
    """API: Okuma trendi"""
    db = DatabaseService()
    try:
        trend = db.get_daily_reading_trend(days=days)
        return jsonify({
            'success': True,
            'data': trend
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

"""Subscribers Routes - PostgreSQL Integrated"""
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from services.database import DatabaseService
from services import (
    create_subscriber,
    update_subscriber,
    delete_subscriber,
    assign_meter_to_subscriber,
    get_subscriber_invoices
)

subscribers_bp = Blueprint('subscribers', __name__)

@subscribers_bp.route('/')
def index():
    """Subscriber management index page"""
    db = DatabaseService()
    try:
        stats = db.get_subscriber_stats()
        return render_template('subscribers/index.html', stats=stats)
    except Exception as e:
        print(f"Error loading subscribers index: {e}")
        return render_template('subscribers/index.html', stats=None)
    finally:
        db.close()

@subscribers_bp.route('/list')
def list():
    """Subscriber list with AG-Grid"""
    db = DatabaseService()
    try:
        subscribers = db.get_all_subscribers()
        stats = db.get_subscriber_stats()
        return render_template('subscribers/list.html', subscribers=subscribers, stats=stats)
    except Exception as e:
        print(f"Error loading subscribers list: {e}")
        return render_template('subscribers/list.html', subscribers=[], stats=None)
    finally:
        db.close()

@subscribers_bp.route('/api/list')
def api_list():
    """API endpoint for subscriber list"""
    db = DatabaseService()
    try:
        subscribers = db.get_all_subscribers()
        return jsonify({
            'success': True,
            'data': subscribers
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@subscribers_bp.route('/<int:id>')
def detail(id):
    """Subscriber detail page"""
    db = DatabaseService()
    try:
        subscriber = db.get_subscriber_detail(id)
        if not subscriber:
            return render_template('errors/404.html'), 404
        
        # Get consumption history
        consumption = db.get_subscriber_consumption(id)
        
        # Get latest readings
        readings = db.get_subscriber_readings(id, limit=10)
        
        # Get invoices
        try:
            invoices = get_subscriber_invoices(id)
        except:
            invoices = []
        
        return render_template('subscribers/detail.html', 
                             subscriber=subscriber,
                             consumption=consumption,
                             readings=readings,
                             invoices=invoices)
    except Exception as e:
        print(f"Error loading subscriber detail: {e}")
        return render_template('errors/500.html'), 500
    finally:
        db.close()

@subscribers_bp.route('/card')
@subscribers_bp.route('/card/<int:id>')
def card(id=None):
    """Subscriber card view"""
    db = DatabaseService()
    try:
        selected_id = id or request.args.get('id', type=int)
        subscriber = db.get_subscriber_detail(selected_id) if selected_id else None
        subscribers = db.get_all_subscribers()

        return render_template(
            'subscribers/card.html',
            subscriber=subscriber,
            subscribers=subscribers,
            selected_id=selected_id
        )
    except Exception as e:
        print(f"Error loading subscriber card: {e}")
        return render_template('subscribers/card.html', subscriber=None, subscribers=[], selected_id=None)
    finally:
        db.close()

@subscribers_bp.route('/add')
def add():
    """Add new subscriber page"""
    db = DatabaseService()
    try:
        tariffs = db.get_tariffs()
        return render_template('subscribers/add.html', tariffs=tariffs)
    except Exception as e:
        print(f"Error loading add subscriber: {e}")
        return render_template('subscribers/add.html', tariffs=[])
    finally:
        db.close()

@subscribers_bp.route('/meters')
def meters():
    """Meter assignment page"""
    db = DatabaseService()
    try:
        meters = db.get_all_meters()
        subscribers = db.get_all_subscribers()
        return render_template('subscribers/meters.html', meters=meters, subscribers=subscribers)
    except Exception as e:
        print(f"Error loading meters: {e}")
        return render_template('subscribers/meters.html', meters=[], subscribers=[])
    finally:
        db.close()

@subscribers_bp.route('/contracts')
def contracts():
    """Subscriber contracts page"""
    db = DatabaseService()
    try:
        # Sözleşme bilgileri olan aboneler
        db.cur.execute("""
            SELECT 
                s.id, s.subscriber_code, s.name, s.sector,
                s.contract_demand, s.status,
                t.name as tariff_name
            FROM subscribers s
            LEFT JOIN tariffs t ON s.tariff_id = t.id
            ORDER BY s.subscriber_code
        """)
        contracts = [dict(row) for row in db.cur.fetchall()]
        
        return render_template('subscribers/contracts.html', contracts=contracts)
    except Exception as e:
        print(f"Error loading contracts: {e}")
        return render_template('subscribers/contracts.html', contracts=[])
    finally:
        db.close()

@subscribers_bp.route('/contracts/<int:id>')
def contract_draft(id):
    """Subscriber contract draft"""
    db = DatabaseService()
    try:
        subscriber = db.get_subscriber_detail(id)
        if not subscriber:
            return render_template('errors/404.html'), 404

        return render_template(
            'subscribers/contract_draft.html',
            subscriber=subscriber,
            today=datetime.now()
        )
    except Exception as e:
        print(f"Error loading contract draft: {e}")
        return render_template('errors/500.html'), 500
    finally:
        db.close()

@subscribers_bp.route('/groups')
def groups():
    """Subscriber groups page"""
    db = DatabaseService()
    try:
        # Sektöre göre gruplandırma
        db.cur.execute("""
            SELECT 
                sector,
                COUNT(*) as subscriber_count,
                SUM(contract_demand) as total_demand
            FROM subscribers
            WHERE status = 'Aktif'
            GROUP BY sector
            ORDER BY subscriber_count DESC
        """)
        groups = [dict(row) for row in db.cur.fetchall()]
        
        return render_template('subscribers/groups.html', groups=groups)
    except Exception as e:
        print(f"Error loading groups: {e}")
        return render_template('subscribers/groups.html', groups=[])
    finally:
        db.close()

@subscribers_bp.route('/<int:id>/edit')
def edit(id):
    """Edit subscriber page"""
    db = DatabaseService()
    try:
        subscriber = db.get_subscriber_detail(id)
        if not subscriber:
            return render_template('errors/404.html'), 404
        
        tariffs = db.get_tariffs()
        return render_template('subscribers/edit.html', subscriber=subscriber, tariffs=tariffs)
    except Exception as e:
        print(f"Error loading edit subscriber: {e}")
        return render_template('errors/500.html'), 500
    finally:
        db.close()

# =============================================================================
# API ENDPOINTS
# =============================================================================

@subscribers_bp.route('/api/create', methods=['POST'])
def api_create():
    """API: Yeni abone oluştur"""
    try:
        data = request.get_json()
        
        # Required fields
        required = ['name', 'tariff_id']
        if not all(k in data for k in required):
            return jsonify({
                'success': False,
                'error': 'name ve tariff_id gerekli'
            }), 400
        
        result = create_subscriber(data)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Abone başarıyla oluşturuldu'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@subscribers_bp.route('/api/update/<int:id>', methods=['PUT', 'POST'])
def api_update(id):
    """API: Abone güncelle"""
    try:
        data = request.get_json()
        result = update_subscriber(id, data)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Abone başarıyla güncellendi'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@subscribers_bp.route('/api/delete/<int:id>', methods=['DELETE', 'POST'])
def api_delete(id):
    """API: Abone sil (soft delete)"""
    try:
        result = delete_subscriber(id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Abone başarıyla silindi'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@subscribers_bp.route('/api/assign-meter', methods=['POST'])
def api_assign_meter():
    """API: Sayaç atama"""
    try:
        data = request.get_json()
        subscriber_id = data.get('subscriber_id')
        meter_id = data.get('meter_id')
        
        if not all([subscriber_id, meter_id]):
            return jsonify({
                'success': False,
                'error': 'subscriber_id ve meter_id gerekli'
            }), 400
        
        result = assign_meter_to_subscriber(subscriber_id, meter_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Sayaç başarıyla atandı'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@subscribers_bp.route('/api/<int:id>/invoices')
def api_invoices(id):
    """API: Abone faturaları"""
    try:
        invoices = get_subscriber_invoices(id)
        return jsonify({
            'success': True,
            'data': invoices
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@subscribers_bp.route('/api/<int:id>/consumption')
def api_consumption(id):
    """API: Abone tüketim geçmişi"""
    db = DatabaseService()
    try:
        days = request.args.get('days', 30, type=int)
        consumption = db.get_subscriber_consumption(id, days=days)
        
        return jsonify({
            'success': True,
            'data': consumption
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@subscribers_bp.route('/api/<int:id>/readings')
def api_readings(id):
    """API: Abone okumaları"""
    db = DatabaseService()
    try:
        limit = request.args.get('limit', 10, type=int)
        readings = db.get_subscriber_readings(id, limit=limit)
        
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

"""
EFYS Route Template
Blueprint boilerplate for new features
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from services.database import DatabaseService

# Blueprint tanımı
FEATURE_NAME_bp = Blueprint('FEATURE_NAME', __name__)


@FEATURE_NAME_bp.route('/')
def index():
    """FEATURE_NAME ana sayfası"""
    db = DatabaseService()
    try:
        # Get stats/summary data
        stats = db.get_FEATURE_NAME_stats()
        
        return render_template('FEATURE_NAME/index.html', 
                             stats=stats)
    except Exception as e:
        print(f"Error loading FEATURE_NAME index: {e}")
        return render_template('FEATURE_NAME/index.html', 
                             stats=None)
    finally:
        db.close()


@FEATURE_NAME_bp.route('/list')
def list():
    """FEATURE_NAME listesi"""
    db = DatabaseService()
    try:
        items = db.get_all_FEATURE_NAME()
        
        return render_template('FEATURE_NAME/list.html', 
                             items=items)
    except Exception as e:
        print(f"Error loading FEATURE_NAME list: {e}")
        return render_template('FEATURE_NAME/list.html', 
                             items=[])
    finally:
        db.close()


@FEATURE_NAME_bp.route('/<int:id>')
def detail(id):
    """FEATURE_NAME detay sayfası"""
    db = DatabaseService()
    try:
        item = db.get_FEATURE_NAME_by_id(id)
        
        if not item:
            return render_template('errors/404.html'), 404
        
        return render_template('FEATURE_NAME/detail.html', 
                             item=item)
    except Exception as e:
        print(f"Error loading FEATURE_NAME detail: {e}")
        return render_template('errors/500.html'), 500
    finally:
        db.close()


# =============================================================================
# API ENDPOINTS
# =============================================================================

@FEATURE_NAME_bp.route('/api/list')
def api_list():
    """API: FEATURE_NAME listesi"""
    db = DatabaseService()
    try:
        items = db.get_all_FEATURE_NAME()
        return jsonify({
            'success': True,
            'data': items,
            'meta': {'count': len(items)}
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()


@FEATURE_NAME_bp.route('/api/create', methods=['POST'])
def api_create():
    """API: FEATURE_NAME oluştur"""
    db = DatabaseService()
    try:
        data = request.get_json()
        
        # Validation
        if not data or 'name' not in data:
            return jsonify({
                'success': False,
                'error': 'name gerekli'
            }), 400
        
        # Create
        item_id = db.create_FEATURE_NAME(data)
        
        return jsonify({
            'success': True,
            'data': {'id': item_id},
            'message': 'Başarıyla oluşturuldu'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()


# =============================================================================
# KAYIT (Register blueprint in routes/__init__.py)
# =============================================================================
"""
# routes/__init__.py içine ekle:

from routes.FEATURE_NAME import FEATURE_NAME_bp

def register_blueprints(app):
    # ... existing blueprints
    app.register_blueprint(FEATURE_NAME_bp, url_prefix='/FEATURE_NAME')
"""

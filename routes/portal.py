"""
Sanayici Portal Routes
Abonelerin kendi verilerini görüntüleyebildiği portal
"""

from flask import Blueprint, render_template, jsonify, request, session
from services.database import DatabaseService
from datetime import datetime, timedelta

portal_bp = Blueprint('portal', __name__, url_prefix='/portal')


def get_db():
    """Get database connection"""
    return DatabaseService()


def get_selected_subscriber_id():
    """Session'dan seçili abone ID'sini al, yoksa ilk aboneyi döndür"""
    if 'selected_subscriber_id' in session:
        return session['selected_subscriber_id']
    
    # İlk aktif aboneyi varsayılan olarak ayarla
    db = get_db()
    try:
        db.cur.execute("SELECT id FROM subscribers WHERE status = 'active' ORDER BY subscriber_code LIMIT 1")
        result = db.cur.fetchone()
        if result:
            session['selected_subscriber_id'] = result['id']
            return result['id']
        return 1  # Fallback
    finally:
        db.close()


def get_all_subscribers():
    """Tüm aktif aboneleri dropdown için al"""
    db = get_db()
    try:
        db.cur.execute("""
            SELECT id, subscriber_code, name 
            FROM subscribers 
            WHERE status = 'active' 
            ORDER BY subscriber_code
        """)
        return [dict(row) for row in db.cur.fetchall()]
    finally:
        db.close()


@portal_bp.route('/')
def index():
    """Portal anasayfa - Sanayici dashboard"""
    db = get_db()
    try:
        subscribers = get_all_subscribers()
        
        # Session'da abone seçimi yoksa modal açılmalı
        show_subscriber_modal = 'selected_subscriber_id' not in session
        
        subscriber_id = get_selected_subscriber_id()
        
        subscriber = db.get_portal_subscriber_data(subscriber_id=subscriber_id)
        consumption = db.get_portal_consumption_data(subscriber_id=subscriber_id)
        reactive = db.get_portal_reactive_data(subscriber_id=subscriber_id)
        invoices = db.get_portal_invoices(subscriber_id=subscriber_id, limit=5)
        daily_consumption = db.get_portal_daily_consumption(subscriber_id=subscriber_id, days=7)
        
        return render_template('portal/index.html',
                             subscriber=subscriber,
                             consumption=consumption,
                             reactive=reactive,
                             invoices=invoices,
                             daily_consumption=daily_consumption,
                             subscribers=subscribers,
                             selected_subscriber_id=subscriber_id,
                             show_subscriber_modal=show_subscriber_modal)
    finally:
        db.close()


@portal_bp.route('/invoices')
def invoices():
    """Fatura listesi"""
    db = get_db()
    try:
        subscribers = get_all_subscribers()
        show_subscriber_modal = 'selected_subscriber_id' not in session
        subscriber_id = get_selected_subscriber_id()
        
        invoices = db.get_portal_invoices(subscriber_id=subscriber_id, limit=20)
        subscriber = db.get_portal_subscriber_data(subscriber_id=subscriber_id)
        return render_template('portal/invoices.html',
                             invoices=invoices,
                             subscriber=subscriber,
                             subscribers=subscribers,
                             selected_subscriber_id=subscriber_id,
                             show_subscriber_modal=show_subscriber_modal)
    finally:
        db.close()


@portal_bp.route('/reports')
def reports():
    """Detaylı raporlar"""
    db = get_db()
    try:
        subscribers = get_all_subscribers()
        show_subscriber_modal = 'selected_subscriber_id' not in session
        subscriber_id = get_selected_subscriber_id()
        
        subscriber = db.get_portal_subscriber_data(subscriber_id=subscriber_id)
        consumption = db.get_portal_consumption_data(subscriber_id=subscriber_id)
        daily_consumption = db.get_portal_daily_consumption(subscriber_id=subscriber_id, days=30)
        return render_template('portal/reports.html',
                             subscriber=subscriber,
                             consumption=consumption,
                             daily_consumption=daily_consumption,
                             subscribers=subscribers,
                             selected_subscriber_id=subscriber_id,
                             show_subscriber_modal=show_subscriber_modal)
    finally:
        db.close()


@portal_bp.route('/energy-quality')
def energy_quality():
    """Enerji kalitesi"""
    db = get_db()
    try:
        subscribers = get_all_subscribers()
        show_subscriber_modal = 'selected_subscriber_id' not in session
        subscriber_id = get_selected_subscriber_id()
        
        subscriber = db.get_portal_subscriber_data(subscriber_id=subscriber_id)
        reactive = db.get_portal_reactive_data(subscriber_id=subscriber_id)
        return render_template('portal/energy-quality.html',
                             subscriber=subscriber,
                             reactive=reactive,
                             subscribers=subscribers,
                             selected_subscriber_id=subscriber_id,
                             show_subscriber_modal=show_subscriber_modal)
    finally:
        db.close()


@portal_bp.route('/api/consumption-chart')
def api_consumption_chart():
    """Günlük tüketim chart verisi"""
    db = get_db()
    try:
        subscriber_id = get_selected_subscriber_id()
        days = request.args.get('days', 7, type=int)
        data = db.get_portal_daily_consumption(subscriber_id=subscriber_id, days=days)
        return jsonify({'success': True, 'data': data})
    finally:
        db.close()


@portal_bp.route('/api/reactive-history')
def api_reactive_history():
    """Reaktif enerji geçmişi"""
    db = get_db()
    try:
        subscriber_id = get_selected_subscriber_id()
        data = db.get_portal_reactive_history(subscriber_id=subscriber_id, days=30)
        return jsonify({'success': True, 'data': data})
    finally:
        db.close()


@portal_bp.route('/select-subscriber/<int:subscriber_id>', methods=['POST'])
def select_subscriber(subscriber_id):
    """Abone seçimini kaydet"""
    session['selected_subscriber_id'] = subscriber_id
    return jsonify({'success': True, 'subscriber_id': subscriber_id})

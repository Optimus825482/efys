"""EFYS Routes Package"""
from flask import Blueprint

def register_blueprints(app):
    """Register all blueprints"""
    from routes.dashboard import dashboard_bp
    from routes.billing import billing_bp
    from routes.monitoring import monitoring_bp
    from routes.subscribers import subscribers_bp
    from routes.reports import reports_bp
    from routes.smart_systems import smart_bp
    from routes.settings import settings_bp
    from routes.portal import portal_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(billing_bp, url_prefix='/billing')
    app.register_blueprint(monitoring_bp, url_prefix='/monitoring')
    app.register_blueprint(subscribers_bp, url_prefix='/subscribers')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(smart_bp, url_prefix='/smart')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(portal_bp)  # /portal prefix in blueprint

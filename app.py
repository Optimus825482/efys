"""
EFYS - Enerji Faturalandırma ve Yönetim Sistemi
Main Flask Application (Updated: 2026-01-29)
"""
from flask import Flask, render_template, redirect, url_for
from config import config
import os

# SQLAlchemy disabled temporarily due to Python 3.13 compatibility
# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()


def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    # db.init_app(app)  # Temporarily disabled
    
    # Register blueprints
    from routes import register_blueprints
    register_blueprints(app)
    
    # Context processors
    @app.context_processor
    def inject_globals():
        return {
            'app_name': app.config['APP_NAME'],
            'app_full_name': app.config['APP_FULL_NAME'],
            'app_version': app.config['APP_VERSION']
        }
    
    # Health check endpoint (for Coolify/Docker)
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring"""
        from services.database import get_db_connection
        
        health_status = {
            'status': 'healthy',
            'app': 'EFYS',
            'version': app.config['APP_VERSION'],
            'database': 'unknown'
        }
        
        # Check database connection
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                conn.close()
                health_status['database'] = 'connected'
            else:
                health_status['database'] = 'disconnected'
                health_status['status'] = 'unhealthy'
        except Exception as e:
            health_status['database'] = f'error: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return health_status, status_code
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500
    
    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    app.run(debug=True, port=5000)

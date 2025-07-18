from flask import Flask
from config.config import Config
from app.models import db
from app.routes.main import main_bp
from app.routes.api import api_bp
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime


def create_app():
    app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
    app.config.from_object(Config)
    register_filters(app)
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    
    # Setup logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/shopify_insights.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Shopify Insights startup')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

from datetime import datetime

def datetime_format(value, format='%Y-%m-%d %H:%M'):
    if not value:
        return 'Never'
    # If value is an ISO 8601 string, try parsing it
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except Exception:
            return value  # Unparseable string, just return as is
    if hasattr(value, 'strftime'):
        return value.strftime(format)
    return str(value)

# Register the filter
def register_filters(app):
    app.jinja_env.filters['datetime_format'] = datetime_format


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
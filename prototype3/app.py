"""
CyberHubs AI Assessment Platform - Main Application
Fully AI-driven cybersecurity assessment with Flask and Jinja2
"""

import os
import logging
from flask import Flask, render_template, session, request
from flask_session import Session
from flask_babel import Babel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import blueprints
from routes.home import home_bp
from routes.assessment import assessment_bp
from routes.dashboard import dashboard_bp
from routes.api import api_bp

# Initialize Babel
babel = Babel()

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'et': 'Eesti',
    'hu': 'Magyar',
    'lt': 'Lietuvių',
    'pl': 'Polski',
    'pt': 'Português',
    'sk': 'Slovenčina',
    'sl': 'Slovenščina'
}

def get_locale():
    """Determine the current locale"""
    # Check if user has set a language preference
    if 'language' in session:
        return session.get('language')
    # Try to use the best match from supported languages
    return request.accept_languages.best_match(SUPPORTED_LANGUAGES.keys()) or 'en'

def create_app():
    """Application factory pattern for Flask app"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY', '')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True') == 'True'
    app.config['LANGUAGES'] = SUPPORTED_LANGUAGES
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'
    
    # Session configuration
    Session(app)
    
    # Initialize Babel
    babel.init_app(app, locale_selector=get_locale)
    
    # Logging configuration
    configure_logging(app)
    
    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(assessment_bp, url_prefix='/assessment')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Error handlers
    register_error_handlers(app)
    
    # Template filters
    register_template_filters(app)
    
    app.logger.info('CyberHubs AI Assessment Platform initialized')
    
    return app

def configure_logging(app):
    """Configure application logging with debugging"""
    if app.config['DEBUG']:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('debug.log'),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('app.log'),
                logging.StreamHandler()
            ]
        )
    
    app.logger.setLevel(logging.DEBUG if app.config['DEBUG'] else logging.INFO)
    app.logger.debug('Logging configured successfully')

def register_error_handlers(app):
    """Register error handlers for common HTTP errors"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f'404 Error: {error}')
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'500 Error: {error}')
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.exception(f'Unhandled exception: {error}')
        return render_template('errors/500.html'), 500

def register_template_filters(app):
    """Register custom Jinja2 template filters"""
    
    @app.template_filter('format_time')
    def format_time(seconds):
        """Format seconds to readable time"""
        if seconds < 60:
            return f"{int(seconds)}s"
        else:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
    
    @app.template_filter('percentage')
    def percentage(value, total):
        """Calculate percentage"""
        if total == 0:
            return 0
        return round((value / total) * 100, 1)

if __name__ == '__main__':
    # Setup logging for startup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    app = create_app()
    
    # Load question bank (hardcoded questions only - no cache needed)
    logger.info('🚀 Loading hardcoded question bank...')
    from services.question_bank import QuestionBank
    question_bank = QuestionBank()
    question_count = question_bank.get_question_count()
    logger.info(f'✅ Question bank loaded: {question_count["total"]} total questions')
    for domain, counts in question_count['by_domain'].items():
        logger.info(f'   {domain}: {counts["total"]} questions ({counts["beginner"]} beginner, {counts["intermediate"]} intermediate, {counts["advanced"]} advanced)')
    
    port = int(os.getenv('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    )

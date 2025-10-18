"""
Home Route Module
Handles main landing page and navigation
"""

import logging
from flask import Blueprint, render_template, session, current_app

logger = logging.getLogger(__name__)

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    """Main landing page"""
    logger.info('Home page accessed')
    logger.debug(f'Session data: {dict(session)}')
    
    try:
        # Get user stats from session if available
        user_stats = session.get('user_stats', {
            'total_assessments': 0,
            'avg_score': 0,
            'badges': []
        })
        
        logger.debug(f'User stats: {user_stats}')
        
        return render_template(
            'home.html',
            user_stats=user_stats,
            app_name=current_app.config.get('APP_NAME', 'CyberHubs Assessment')
        )
    
    except Exception as e:
        logger.exception(f'Error rendering home page: {str(e)}')
        return render_template('errors/500.html'), 500

@home_bp.route('/about')
def about():
    """About page"""
    logger.info('About page accessed')
    
    try:
        return render_template('about.html')
    except Exception as e:
        logger.exception(f'Error rendering about page: {str(e)}')
        return render_template('errors/500.html'), 500

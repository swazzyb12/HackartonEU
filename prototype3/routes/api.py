"""
API Route Module
Handles JSON API endpoints
"""

import logging
from flask import Blueprint, jsonify, request, session
from services import get_gemini_service, get_assessment_service

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    logger.debug('Health check requested')
    return jsonify({
        'status': 'healthy',
        'service': 'CyberHubs AI Assessment'
    })

@api_bp.route('/generate-question', methods=['POST'])
def generate_question():
    """API endpoint to generate a question"""
    logger.info('Question generation API called')
    
    try:
        data = request.get_json()
        domain = data.get('domain', 'network-security')
        difficulty = data.get('difficulty', 'beginner')
        
        logger.debug(f'Generating question via API - Domain: {domain}, Difficulty: {difficulty}')
        
        gemini_service = get_gemini_service()
        question = gemini_service.generate_question(domain, difficulty)
        
        if question:
            logger.info('Question generated successfully via API')
            return jsonify({
                'success': True,
                'question': question
            })
        else:
            logger.warning('Failed to generate question via API')
            return jsonify({
                'success': False,
                'error': 'Failed to generate question'
            }), 500
    
    except Exception as e:
        logger.exception(f'Error in generate_question API: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get user statistics"""
    logger.info('Stats API called')
    
    try:
        user_stats = session.get('user_stats', {
            'total_assessments': 0,
            'avg_score': 0,
            'badges': []
        })
        
        logger.debug(f'Returning stats: {user_stats}')
        
        return jsonify({
            'success': True,
            'stats': user_stats
        })
    
    except Exception as e:
        logger.exception(f'Error in get_stats API: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/clear-session', methods=['POST'])
def clear_session():
    """Clear user session (for testing/debugging)"""
    logger.info('Session clear requested')
    
    try:
        session.clear()
        logger.info('Session cleared successfully')
        
        return jsonify({
            'success': True,
            'message': 'Session cleared'
        })
    
    except Exception as e:
        logger.exception(f'Error clearing session: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/set-language/<language>', methods=['POST'])
def set_language(language):
    """Set user language preference"""
    logger.info(f'Language preference change requested: {language}')
    
    from app import SUPPORTED_LANGUAGES
    
    try:
        if language in SUPPORTED_LANGUAGES:
            session['language'] = language
            logger.info(f'Language set to: {language}')
            return jsonify({
                'success': True,
                'message': f'Language set to {SUPPORTED_LANGUAGES[language]}',
                'language': language
            })
        else:
            logger.warning(f'Unsupported language requested: {language}')
            return jsonify({
                'success': False,
                'error': 'Unsupported language'
            }), 400
    
    except Exception as e:
        logger.exception(f'Error setting language: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.errorhandler(404)
def api_not_found(error):
    """API 404 handler"""
    logger.warning(f'API endpoint not found: {request.path}')
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@api_bp.errorhandler(500)
def api_internal_error(error):
    """API 500 handler"""
    logger.error(f'API internal error: {str(error)}')
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

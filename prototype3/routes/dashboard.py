"""
Dashboard Route Module
Handles user dashboard and statistics
"""

import logging
from flask import Blueprint, render_template, session, redirect, url_for
from services import all_badges_with_earned

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    """Main dashboard page"""
    logger.info('Dashboard accessed')
    
    try:
        # Get user stats from session
        user_stats = session.get('user_stats', {
            'total_assessments': 0,
            'avg_score': 0,
            'badges': [],
            'history': []
        })
        
        logger.debug(f'User stats: Total assessments: {user_stats.get("total_assessments", 0)}')
        
        # Calculate additional metrics
        history = user_stats.get('history', [])
        if history:
            # Recent assessments
            recent_assessments = sorted(
                history,
                key=lambda x: x['date'],
                reverse=True
            )[:5]
            
            # Domain performance
            domain_stats = calculate_domain_stats(history)
            
            # Progress over time
            progress_data = calculate_progress(history)
            
            # Best score overall
            best_score = max((item.get('score', 0) for item in history), default=0)
            
            logger.debug(f'Dashboard metrics calculated for {len(user_stats["history"])} assessments')
        else:
            recent_assessments = []
            domain_stats = {}
            progress_data = []
            best_score = 0
            logger.debug('No assessment history found')

        # Build consolidated stats object expected by template
        stats = {
            'total_assessments': user_stats.get('total_assessments', 0),
            'avg_score': user_stats.get('avg_score', 0),
            'best_score': best_score,
            'badges': user_stats.get('badges', []),
            'by_domain': domain_stats,
        }

        return render_template(
            'dashboard/index.html',
            user_stats=user_stats,
            stats=stats,
            recent_assessments=recent_assessments,
            domain_stats=domain_stats,
            progress_data=progress_data
        )
    
    except Exception as e:
        logger.exception(f'Error displaying dashboard: {str(e)}')
        return render_template('errors/500.html'), 500

@dashboard_bp.route('/history')
def history():
    """Assessment history page"""
    logger.info('History page accessed')
    
    try:
        user_stats = session.get('user_stats', {'history': []})
        full_history = sorted(
            user_stats.get('history', []),
            key=lambda x: x['date'],
            reverse=True
        )

        # Pagination params
        from flask import request
        try:
            page = int(request.args.get('page', 1))
        except ValueError:
            page = 1
        try:
            page_size = int(request.args.get('page_size', 10))
        except ValueError:
            page_size = 10
        page = max(1, page)
        page_size = max(1, min(page_size, 100))

        total_items = len(full_history)
        page_count = (total_items + page_size - 1) // page_size if total_items else 1
        if page > page_count:
            page = page_count

        start = (page - 1) * page_size
        end = start + page_size
        history_slice = full_history[start:end]

        logger.debug(f'Showing {len(history_slice)} of {total_items} historical assessments (page {page}/{page_count})')
        
        return render_template(
            'dashboard/history.html',
            history=history_slice,
            page=page,
            page_size=page_size,
            page_count=page_count,
        )
    
    except Exception as e:
        logger.exception(f'Error displaying history: {str(e)}')
        return render_template('errors/500.html'), 500

@dashboard_bp.route('/badges')
def badges():
    """Badges and achievements page"""
    logger.info('Badges page accessed')
    
    try:
        user_stats = session.get('user_stats', {'badges': []})
        badges_list = all_badges_with_earned(user_stats)
        logger.debug(f'User has earned {len(user_stats.get("badges", []))} badges')

        # Convert to a dict keyed by id for template backward-compat
        badges_by_id = {b['id']: b for b in badges_list}

        return render_template(
            'dashboard/badges.html',
            badges=badges_by_id,
            earned_count=len([b for b in badges_list if b['earned']])
        )
    
    except Exception as e:
        logger.exception(f'Error displaying badges: {str(e)}')
        return render_template('errors/500.html'), 500

def calculate_domain_stats(history):
    """Calculate performance statistics by domain"""
    logger.debug('Calculating domain statistics')
    
    domain_stats = {}
    
    for assessment in history:
        domain = assessment['domain']
        
        if domain not in domain_stats:
            domain_stats[domain] = {
                'count': 0,
                'total_score': 0,
                'avg_score': 0,
                'best_score': 0
            }
        
        domain_stats[domain]['count'] += 1
        domain_stats[domain]['total_score'] += assessment['score']
        domain_stats[domain]['best_score'] = max(
            domain_stats[domain]['best_score'],
            assessment['score']
        )
    
    # Calculate averages
    for domain in domain_stats:
        stats = domain_stats[domain]
        stats['avg_score'] = round(stats['total_score'] / stats['count'], 2)
    
    logger.debug(f'Domain stats calculated for {len(domain_stats)} domains')
    return domain_stats

def calculate_progress(history):
    """Calculate progress over time"""
    logger.debug('Calculating progress data')
    
    if not history:
        return []
    
    # Sort by date
    sorted_history = sorted(history, key=lambda x: x['date'])
    
    # Calculate running average
    progress = []
    total_score = 0
    
    for i, assessment in enumerate(sorted_history, 1):
        total_score += assessment['score']
        avg = round(total_score / i, 2)
        
        progress.append({
            'assessment_number': i,
            'score': assessment['score'],
            'average': avg,
            'date': assessment['date']
        })
    
    logger.debug(f'Progress data calculated for {len(progress)} assessments')
    return progress

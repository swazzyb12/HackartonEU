"""
Assessment Route Module
Handles assessment creation, questions, and submissions
"""

import logging
import time
from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
from services import (
    get_gemini_service,
    get_assessment_service,
    QuestionBank,
    evaluate_badges,
    BADGE_DEFS,
)

logger = logging.getLogger(__name__)

assessment_bp = Blueprint('assessment', __name__)

# Global question bank instance
_question_bank = None

def get_question_bank():
    """Get or create the global question bank instance"""
    global _question_bank
    if _question_bank is None:
        _question_bank = QuestionBank()
    return _question_bank

@assessment_bp.route('/start', methods=['GET', 'POST'])
def start():
    """Start a new assessment"""
    logger.info('Assessment start page accessed')
    
    if request.method == 'GET':
        # Check if domain is provided in URL (from home page)
        domain = request.args.get('domain')
        
        if domain:
            # Domain selected from home page - show quick start confirmation
            logger.debug(f'Domain pre-selected: {domain}')
            return render_template('assessment/start.html', selected_domain=domain)
        else:
            # No domain - show full selection page
            logger.debug('Showing domain selection')
            return render_template('assessment/start.html')
    
    # Handle POST - create new assessment
    try:
        domain = request.form.get('domain', 'network-security')
        num_questions = int(request.form.get('num_questions', 10))
        
        logger.info(f'Creating ADAPTIVE assessment - Domain: {domain}, Questions: {num_questions}')
        
        # Create assessment (no difficulty - it's adaptive!)
        assessment_service = get_assessment_service()
        assessment = assessment_service.create_assessment(domain)
        assessment['total_questions'] = num_questions
        
        # Store in session
        session['current_assessment'] = assessment
        session['question_start_time'] = None
        
        logger.debug(f'Adaptive assessment created with ID: {assessment["id"]}')
        
        # Redirect to questions
        return redirect(url_for('assessment.question'))
    
    except Exception as e:
        logger.exception(f'Error starting assessment: {str(e)}')
        return render_template('errors/500.html'), 500

@assessment_bp.route('/question', methods=['GET', 'POST'])
def question():
    """Display current question or generate next one"""
    logger.info('Question page accessed')
    
    # Check if assessment exists
    if 'current_assessment' not in session:
        logger.warning('No active assessment found, redirecting to start')
        return redirect(url_for('assessment.start'))
    
    assessment = session['current_assessment']
    current_question_index = assessment['current_question']
    
    logger.debug(f'Current question index: {current_question_index}')
    
    # Handle answer submission
    if request.method == 'POST':
        return handle_answer_submission(assessment)
    
    # Check if we need to generate a new question
    if current_question_index >= len(assessment['questions']):
        logger.info('Generating new question')
        return generate_next_question(assessment)
    
    # Display current question
    try:
        question_data = assessment['questions'][current_question_index]
        
        # Set question start time if not already set
        if session.get('question_start_time') is None:
            session['question_start_time'] = time.time()
            logger.debug('Question timer started')
        
        return render_template(
            'assessment/question.html',
            question=question_data,
            question_id=question_data.get('id', ''),
            start_time=session.get('question_start_time', time.time()),
            current_question=current_question_index,
            total_questions=assessment.get('total_questions', 10),
            assessment=assessment
        )
    
    except Exception as e:
        logger.exception(f'Error displaying question: {str(e)}')
        return render_template('errors/500.html'), 500

def generate_next_question(assessment):
    """Get the next question from hardcoded question bank"""
    logger.info('Getting next question from hardcoded bank')
    
    try:
        question_bank = get_question_bank()
        assessment_service = get_assessment_service()
        
        # Get question from hardcoded bank
        logger.debug(f'Retrieving question - Domain: {assessment["domain"]}, Difficulty: {assessment["difficulty"]}')
        question = question_bank.get_question(
            domain=assessment['domain'],
            difficulty=assessment['difficulty']
        )
        
        if not question:
            logger.error(f'No questions available for {assessment["domain"]} at {assessment["difficulty"]} difficulty')
            return render_template(
                'assessment/error.html',
                error=f'No questions available for {assessment["domain"]} at {assessment["difficulty"]} difficulty. Please try a different domain or difficulty.'
            )
        
        logger.info(f'✅ Question retrieved: {question.get("title")}')
        
        # Add question to assessment
        assessment_service.add_question(assessment, question)
        
        # Update session
        session['current_assessment'] = assessment
        session['question_start_time'] = time.time()
        
        # Redirect to display the question
        return redirect(url_for('assessment.question'))
    
    except Exception as e:
        logger.exception(f'Error generating question: {str(e)}')
        return render_template('errors/500.html'), 500

def handle_answer_submission(assessment):
    """Handle answer submission"""
    logger.info('Processing answer submission')
    
    try:
        question_id = request.form.get('question_id')
        answer_index = int(request.form.get('answer'))
        
        # Calculate time taken
        start_time = session.get('question_start_time')
        if start_time:
            time_taken = time.time() - start_time
        else:
            time_taken = 0
            logger.warning('No start time found for question')
        
        logger.debug(f'Answer: {answer_index}, Time taken: {time_taken}s, Question ID: {question_id}')
        
        # Submit answer
        assessment_service = get_assessment_service()
        result = assessment_service.submit_answer(
            assessment,
            question_id,
            answer_index,
            time_taken
        )
        
        # Check for errors
        if 'error' in result:
            logger.error(f'Error submitting answer: {result["error"]}')
            return render_template('assessment/error.html', error=result['error']), 400
        
        # Update session
        session['current_assessment'] = assessment
        session['question_start_time'] = None
        
        logger.info(f'Answer processed - Correct: {result.get("is_correct")}')
        
        # Check if assessment is complete
        total_questions = assessment.get('total_questions', 10)
        if assessment['current_question'] >= total_questions:
            logger.info('Assessment complete, redirecting to results')
            return redirect(url_for('assessment.results'))
        
        # Get current question for feedback display
        current_question_index = assessment['current_question'] - 1  # -1 because we already incremented
        question = assessment['questions'][current_question_index]
        
        # Calculate current score
        correct_answers = sum(1 for ans in assessment['answers'] if ans['is_correct'])
        score = round((correct_answers / len(assessment['answers'])) * 100, 1)
        
        # Show feedback then continue
        return render_template(
            'assessment/feedback.html',
            feedback=result,
            question=question,
            user_answer=answer_index,
            time_taken=time_taken,
            score=score,
            current_question=assessment['current_question'],
            total_questions=total_questions,
            assessment=assessment
        )
    
    except Exception as e:
        logger.exception(f'Error handling answer submission: {str(e)}')
        return render_template('errors/500.html'), 500

@assessment_bp.route('/results')
def results():
    """Display assessment results with AI-generated summary and recommendations"""
    logger.info('Results page accessed')
    
    # Check if assessment exists
    if 'current_assessment' not in session:
        logger.warning('No assessment found, redirecting to start')
        return redirect(url_for('assessment.start'))
    
    try:
        assessment = session['current_assessment']
        assessment_service = get_assessment_service()
        
        # Calculate results
        logger.info(f'Calculating results for assessment {assessment["id"]}')
        results_data = assessment_service.calculate_results(assessment)
        
        # Get performance level
        performance_level = assessment_service.get_performance_level(results_data['score'])
        results_data['performance_level'] = performance_level
        
        # Get recommendation
        recommendation = assessment_service.get_recommended_difficulty(
            results_data['score'],
            assessment['difficulty']
        )
        results_data['recommended_difficulty'] = recommendation
        
        logger.info(f'Results calculated - Score: {results_data["score"]}%, Level: {performance_level}')
        
        # Generate AI summary and recommendations
        logger.info('Generating AI-powered summary and recommendations')
        gemini_service = get_gemini_service()
        
        # Generate summary
        summary = gemini_service.generate_assessment_summary(results_data)
        if summary:
            results_data['ai_summary'] = summary
            logger.info('✅ AI summary generated')
        else:
            logger.warning('AI summary generation failed - using fallback')
            results_data['ai_summary'] = None
        
        # Generate recommendations
        recommendations = gemini_service.generate_recommendations(results_data)
        if recommendations:
            results_data['ai_recommendations'] = recommendations
            logger.info(f'✅ Generated {len(recommendations)} AI recommendations')
        else:
            logger.warning('AI recommendations generation failed - using fallback')
            results_data['ai_recommendations'] = []

        # Update user stats and evaluate badges
        newly_earned = update_user_stats(results_data)
        # Map newly earned ids to badge definitions for display
        badge_map = {b['id']: b for b in BADGE_DEFS}
        newly_badges = [badge_map[b] for b in newly_earned if b in badge_map]

        return render_template(
            'assessment/results.html',
            results=results_data,
            assessment=assessment,
            newly_badges=newly_badges,
        )
    
    except Exception as e:
        logger.exception(f'Error displaying results: {str(e)}')
        return render_template('errors/500.html'), 500

def update_user_stats(results_data):
    """Update user statistics in session"""
    logger.debug('Updating user stats')
    
    try:
        user_stats = session.get('user_stats', {
            'total_assessments': 0,
            'total_score': 0,
            'avg_score': 0,
            'badges': [],
            'history': []
        })
        
        # Update stats
        user_stats['total_assessments'] += 1
        user_stats['total_score'] += results_data['score']
        user_stats['avg_score'] = round(
            user_stats['total_score'] / user_stats['total_assessments'],
            2
        )
        
        # Add to history
        user_stats['history'].append({
            'date': results_data['completion_date'],
            'domain': results_data['domain'],
            'difficulty': results_data.get('difficulty', ''),
            'score': results_data['score'],
            'performance_level': results_data['performance_level']
        })
        
        # Award badges using the badge service
        try:
            newly_earned = evaluate_badges(user_stats, results_data)
        except Exception as e:
            logger.exception(f'Badge evaluation failed: {e}')
            newly_earned = []
        
        if newly_earned:
            existing = set(user_stats.get('badges', []))
            for b in newly_earned:
                if b not in existing:
                    user_stats['badges'].append(b)
            logger.info(f"Badges awarded: {', '.join(newly_earned)}")

        # Update session
        session['user_stats'] = user_stats

        logger.debug(f'User stats updated: {user_stats}')
        # Return newly earned badges to show on results page
        return newly_earned

    except Exception as e:
        logger.exception(f'Error updating user stats: {str(e)}')
        return []

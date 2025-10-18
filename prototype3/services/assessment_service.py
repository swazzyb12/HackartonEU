"""
Assessment Service Module
Handles assessment logic, scoring, and data management
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class AssessmentService:
    """Service class for managing assessments"""
    
    def __init__(self):
        """Initialize assessment service"""
        logger.debug('Assessment service initialized')
    
    def create_assessment(self, domain: str, difficulty: str = None, user_id: Optional[str] = None) -> Dict:
        """
        Create a new assessment session with adaptive difficulty
        
        Args:
            domain: Assessment domain
            difficulty: Initial difficulty level (deprecated - now adaptive)
            user_id: Optional user identifier
        
        Returns:
            Assessment session dictionary
        """
        assessment_id = str(uuid.uuid4())
        # Start at intermediate for adaptive assessment
        initial_difficulty = 'intermediate'
        logger.info(f'Creating new ADAPTIVE assessment: {assessment_id} - Domain: {domain}, Starting at: {initial_difficulty}')
        
        assessment = {
            'id': assessment_id,
            'domain': domain,
            'difficulty': initial_difficulty,  # Current difficulty (adaptive)
            'user_id': user_id,
            'questions': [],
            'answers': [],
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'status': 'in_progress',
            'current_question': 0,
            'adaptive_mode': True,
            'difficulty_history': [initial_difficulty],  # Track difficulty changes
            'performance_streak': 0  # Track consecutive correct/incorrect
        }
        
        logger.debug(f'Adaptive assessment created: {assessment_id}')
        return assessment
    
    def add_question(self, assessment: Dict, question: Dict) -> Dict:
        """
        Add a question to the assessment
        
        Args:
            assessment: Assessment session dictionary
            question: Question dictionary
        
        Returns:
            Updated assessment
        """
        question_id = str(uuid.uuid4())
        question['id'] = question_id
        question['timestamp'] = datetime.now().isoformat()
        
        assessment['questions'].append(question)
        logger.debug(f'Added question {question_id} to assessment {assessment["id"]}')
        
        return assessment
    
    def submit_answer(self, assessment: Dict, question_id: str, answer_index: int, time_taken: float) -> Dict:
        """
        Submit an answer for a question and adjust difficulty adaptively
        
        Args:
            assessment: Assessment session dictionary
            question_id: ID of the question being answered
            answer_index: Index of the selected answer
            time_taken: Time taken to answer in seconds
        
        Returns:
            Answer result dictionary
        """
        logger.debug(f'Submitting answer for question {question_id}')
        
        # Find the question
        question = next((q for q in assessment['questions'] if q['id'] == question_id), None)
        
        if not question:
            logger.error(f'Question not found: {question_id}')
            return {'error': 'Question not found'}
        
        # Check if answer is correct
        is_correct = answer_index == question['correct']
        
        answer = {
            'question_id': question_id,
            'answer_index': answer_index,
            'is_correct': is_correct,
            'time_taken': time_taken,
            'timestamp': datetime.now().isoformat(),
            'difficulty_at_time': assessment['difficulty']
        }
        
        assessment['answers'].append(answer)
        assessment['current_question'] += 1
        
        # Adaptive difficulty adjustment
        if assessment.get('adaptive_mode', False):
            self._adjust_difficulty(assessment, is_correct, time_taken)
        
        logger.info(f'Answer submitted - Correct: {is_correct}, Time: {time_taken}s, New difficulty: {assessment["difficulty"]}')
        
        return {
            'is_correct': is_correct,
            'correct_answer': question['correct'],
            'explanation': question.get('explanation', ''),
            'learning_points': question.get('learningPoints', []),
            'sources': question.get('sources', [])
        }
    
    def calculate_results(self, assessment: Dict) -> Dict:
        """
        Calculate assessment results and statistics
        
        Args:
            assessment: Completed assessment session
        
        Returns:
            Results dictionary with score and statistics
        """
        logger.info(f'Calculating results for assessment {assessment["id"]}')
        
        total_questions = len(assessment['questions'])
        total_answers = len(assessment['answers'])
        
        if total_questions == 0:
            logger.warning('No questions in assessment')
            return {'error': 'No questions in assessment'}
        
        # Calculate basic metrics
        correct_answers = sum(1 for ans in assessment['answers'] if ans['is_correct'])
        score = round((correct_answers / total_questions) * 100, 2)
        
        # Calculate time metrics
        total_time = sum(ans['time_taken'] for ans in assessment['answers'])
        avg_time = round(total_time / total_answers, 2) if total_answers > 0 else 0
        
        # Find fastest and slowest questions
        times = [ans['time_taken'] for ans in assessment['answers']]
        fastest_time = min(times) if times else 0
        slowest_time = max(times) if times else 0
        
        # Calculate difficulty progression
        difficulty_performance = self._analyze_difficulty(assessment)
        
        results = {
            'assessment_id': assessment['id'],
            'domain': assessment['domain'],
            'difficulty': assessment['difficulty'],
            'total_questions': total_questions,
            'answered': total_answers,
            'correct_answers': correct_answers,
            'correct': correct_answers,
            'incorrect': total_answers - correct_answers,
            'score': score,
            'total_time_seconds': round(total_time, 2),
            'total_time': round(total_time, 2),
            'avg_time_per_question': avg_time,
            'avg_time': avg_time,
            'fastest_time': round(fastest_time, 2),
            'slowest_time': round(slowest_time, 2),
            'difficulty_performance': difficulty_performance,
            'difficulty_history': assessment.get('difficulty_history', [assessment['difficulty']]),
            'adaptive_mode': assessment.get('adaptive_mode', False),
            'performance_streak': assessment.get('performance_streak', 0),
            'completion_date': datetime.now().isoformat()
        }
        
        logger.info(f'Results calculated - Score: {score}%, Correct: {correct_answers}/{total_questions}')
        logger.debug(f'Difficulty progression: {results["difficulty_history"]}')
        logger.debug(f'Results details: {results}')
        
        return results
    
    def _analyze_difficulty(self, assessment: Dict) -> Dict:
        """Analyze performance across different question difficulties"""
        
        difficulty_stats = {
            'beginner': {'total': 0, 'correct': 0},
            'intermediate': {'total': 0, 'correct': 0},
            'advanced': {'total': 0, 'correct': 0}
        }
        
        for i, question in enumerate(assessment['questions']):
            if i >= len(assessment['answers']):
                continue
                
            diff = question.get('difficulty', 'intermediate')
            answer = assessment['answers'][i]
            
            if diff in difficulty_stats:
                difficulty_stats[diff]['total'] += 1
                if answer['is_correct']:
                    difficulty_stats[diff]['correct'] += 1
        
        # Calculate percentages
        for diff in difficulty_stats:
            total = difficulty_stats[diff]['total']
            if total > 0:
                correct = difficulty_stats[diff]['correct']
                difficulty_stats[diff]['percentage'] = round((correct / total) * 100, 1)
            else:
                difficulty_stats[diff]['percentage'] = 0
        
        logger.debug(f'Difficulty analysis: {difficulty_stats}')
        return difficulty_stats
    
    def get_performance_level(self, score: float) -> str:
        """
        Determine performance level based on score
        
        Args:
            score: Assessment score percentage
        
        Returns:
            Performance level string
        """
        if score >= 90:
            return 'Expert'
        elif score >= 75:
            return 'Advanced'
        elif score >= 60:
            return 'Intermediate'
        elif score >= 40:
            return 'Beginner'
        else:
            return 'Novice'
    
    def get_recommended_difficulty(self, score: float, current_difficulty: str) -> str:
        """
        Recommend next difficulty level based on performance
        
        Args:
            score: Assessment score percentage
            current_difficulty: Current difficulty level
        
        Returns:
            Recommended difficulty level
        """
        logger.debug(f'Getting recommendation - Score: {score}, Current: {current_difficulty}')
        
        if score >= 85 and current_difficulty == 'beginner':
            recommendation = 'intermediate'
        elif score >= 85 and current_difficulty == 'intermediate':
            recommendation = 'advanced'
        elif score < 50 and current_difficulty == 'advanced':
            recommendation = 'intermediate'
        elif score < 50 and current_difficulty == 'intermediate':
            recommendation = 'beginner'
        else:
            recommendation = current_difficulty
        
        logger.info(f'Recommended difficulty: {recommendation}')
        return recommendation
    
    def _adjust_difficulty(self, assessment: Dict, is_correct: bool, time_taken: float) -> None:
        """
        Adaptively adjust difficulty based on performance
        Uses a streak-based system:
        - 2 correct in a row (quick) -> increase difficulty
        - 2 incorrect in a row -> decrease difficulty
        
        Args:
            assessment: Assessment session dictionary
            is_correct: Whether the answer was correct
            time_taken: Time taken to answer
        """
        current_difficulty = assessment['difficulty']
        streak = assessment.get('performance_streak', 0)
        
        # Quick answer threshold (in seconds)
        QUICK_ANSWER_THRESHOLD = 30
        
        logger.debug(f'Adjusting difficulty - Current: {current_difficulty}, Streak: {streak}, Correct: {is_correct}, Time: {time_taken}s')
        
        # Update streak
        if is_correct:
            # Correct answer - increase positive streak or reset negative
            if streak >= 0:
                streak += 1
                # Bonus for quick correct answers
                if time_taken < QUICK_ANSWER_THRESHOLD:
                    streak += 0.5
            else:
                streak = 1
        else:
            # Incorrect answer - increase negative streak or reset positive
            if streak <= 0:
                streak -= 1
            else:
                streak = -1
        
        assessment['performance_streak'] = streak
        
        # Determine if difficulty should change
        new_difficulty = current_difficulty
        
        # Increase difficulty after 2 correct answers (or 1.5 quick correct)
        if streak >= 2:
            if current_difficulty == 'beginner':
                new_difficulty = 'intermediate'
                logger.info('📈 Increasing difficulty: beginner → intermediate (strong performance)')
            elif current_difficulty == 'intermediate':
                new_difficulty = 'advanced'
                logger.info('📈 Increasing difficulty: intermediate → advanced (strong performance)')
            # Reset streak after difficulty increase
            assessment['performance_streak'] = 0
        
        # Decrease difficulty after 2 incorrect answers
        elif streak <= -2:
            if current_difficulty == 'advanced':
                new_difficulty = 'intermediate'
                logger.info('📉 Decreasing difficulty: advanced → intermediate (struggling)')
            elif current_difficulty == 'intermediate':
                new_difficulty = 'beginner'
                logger.info('📉 Decreasing difficulty: intermediate → beginner (struggling)')
            # Reset streak after difficulty decrease
            assessment['performance_streak'] = 0
        
        # Update difficulty if changed
        if new_difficulty != current_difficulty:
            assessment['difficulty'] = new_difficulty
            assessment['difficulty_history'].append(new_difficulty)
            logger.info(f'Difficulty adjusted: {current_difficulty} → {new_difficulty}')
        else:
            logger.debug(f'Difficulty unchanged: {current_difficulty} (streak: {streak})')

# Singleton instance
_assessment_service = None

def get_assessment_service() -> AssessmentService:
    """Get or create singleton assessment service instance"""
    global _assessment_service
    
    if _assessment_service is None:
        logger.debug('Creating new assessment service instance')
        _assessment_service = AssessmentService()
    
    return _assessment_service

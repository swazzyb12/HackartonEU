"""
Simple Question Bank Service - Hardcoded Questions Only
Loads questions from questions.json file
"""

import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class QuestionBank:
    """Service for loading and managing hardcoded questions from JSON"""
    
    def __init__(self, questions_file: str = 'questions.json'):
        """
        Initialize the question bank
        
        Args:
            questions_file: Path to the questions JSON file
        """
        self.questions_file = questions_file
        self.questions = {}
        self.used_questions = {}  # Track used questions per domain/difficulty
        
        # Load questions at initialization
        self._load_questions()
    
    def _load_questions(self) -> bool:
        """
        Load questions from JSON file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Find questions.json in current directory or parent
            questions_path = Path(self.questions_file)
            
            if not questions_path.exists():
                # Try parent directory
                questions_path = Path(__file__).parent.parent / self.questions_file
            
            if not questions_path.exists():
                logger.error(f'Questions file not found: {self.questions_file}')
                return False
            
            logger.info(f'Loading questions from: {questions_path}')
            
            with open(questions_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.questions = data.get('questions', {})
            
            # Count questions
            total_count = sum(len(q_list) for q_list in self.questions.values())
            logger.info(f'Loaded {total_count} questions from {len(self.questions)} categories')
            
            # Log counts per domain
            domain_counts = {}
            for key in self.questions.keys():
                domain = key.split('_')[0]
                domain_counts[domain] = domain_counts.get(domain, 0) + len(self.questions[key])
            
            for domain, count in domain_counts.items():
                logger.info(f'   {domain}: {count} questions')
            
            return True
        
        except json.JSONDecodeError as e:
            logger.exception(f'Invalid JSON in questions file: {e}')
            return False
        except Exception as e:
            logger.exception(f'Error loading questions: {e}')
            return False
    
    def get_question(self, domain: str, difficulty: str) -> Optional[Dict]:
        """
        Get a random unused question for the specified domain and difficulty
        
        Args:
            domain: Question domain (e.g., 'network-security')
            difficulty: Question difficulty ('beginner', 'intermediate', 'advanced')
        
        Returns:
            Question dictionary or None if no questions available
        """
        key = f'{domain}_{difficulty}'
        
        if key not in self.questions:
            logger.warning(f'No questions found for {key}')
            return None
        
        # Get list of questions for this category
        available_questions = self.questions[key]
        
        if not available_questions:
            logger.warning(f'Empty question list for {key}')
            return None
        
        # Initialize used questions tracking for this key
        if key not in self.used_questions:
            self.used_questions[key] = set()
        
        # Find unused questions
        unused_questions = [
            q for i, q in enumerate(available_questions)
            if i not in self.used_questions[key]
        ]
        
        # If all questions used, reset for this category
        if not unused_questions:
            logger.info(f'All questions used for {key}, resetting...')
            self.used_questions[key] = set()
            unused_questions = available_questions
        
        # Select random unused question
        question = random.choice(unused_questions)
        
        # Mark as used
        question_index = available_questions.index(question)
        self.used_questions[key].add(question_index)
        
        logger.debug(f'Selected question from {key}: {question.get("title", "Untitled")}')
        logger.debug(f'   Used: {len(self.used_questions[key])}/{len(available_questions)}')
        
        # Return a copy to avoid modification
        return question.copy()
    
    def get_question_count(self) -> Dict:
        """
        Get statistics about available questions
        
        Returns:
            Dictionary with question counts by domain, difficulty, and total
        """
        stats = {
            'total': 0,
            'by_domain': {},
            'by_difficulty': {
                'beginner': 0,
                'intermediate': 0,
                'advanced': 0
            }
        }
        
        for key, questions in self.questions.items():
            count = len(questions)
            stats['total'] += count
            
            # Parse domain and difficulty
            parts = key.split('_')
            if len(parts) == 2:
                domain, difficulty = parts
                
                # Count by domain
                if domain not in stats['by_domain']:
                    stats['by_domain'][domain] = {
                        'total': 0,
                        'beginner': 0,
                        'intermediate': 0,
                        'advanced': 0
                    }
                
                stats['by_domain'][domain]['total'] += count
                stats['by_domain'][domain][difficulty] = count
                
                # Count by difficulty
                if difficulty in stats['by_difficulty']:
                    stats['by_difficulty'][difficulty] += count
        
        return stats
    
    def reset_used_questions(self, domain: Optional[str] = None, difficulty: Optional[str] = None):
        """
        Reset used question tracking
        
        Args:
            domain: If provided, reset only for this domain
            difficulty: If provided along with domain, reset only for this domain/difficulty
        """
        if domain and difficulty:
            key = f'{domain}_{difficulty}'
            if key in self.used_questions:
                self.used_questions[key] = set()
                logger.info(f'Reset used questions for {key}')
        elif domain:
            # Reset all difficulties for this domain
            for key in list(self.used_questions.keys()):
                if key.startswith(f'{domain}_'):
                    self.used_questions[key] = set()
            logger.info(f'Reset used questions for domain: {domain}')
        else:
            # Reset all
            self.used_questions = {}
            logger.info('Reset all used questions')

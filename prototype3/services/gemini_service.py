"""
Gemini AI Service - Summary and Recommendations Only
Generates personalized feedback based on assessment results
"""

import os
import logging
import google.generativeai as genai
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for generating AI-powered summaries and recommendations"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini service with API key"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            logger.warning('Gemini API key not configured - AI summaries will be disabled')
            self.model = None
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
            logger.info('✅ Gemini AI service initialized for summaries/recommendations')
        except Exception as e:
            logger.error(f'Failed to initialize Gemini: {e}')
            self.model = None
    
    def generate_assessment_summary(self, assessment_data: Dict) -> Optional[str]:
        """
        Generate a personalized summary of the assessment performance
        
        Args:
            assessment_data: Dictionary containing assessment results
        
        Returns:
            Summary text or None if generation fails
        """
        if not self.model:
            return self._get_fallback_summary(assessment_data)
        
        try:
            prompt = self._build_summary_prompt(assessment_data)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500,
                )
            )
            
            summary = response.text.strip()
            logger.info('✅ Generated AI summary')
            return summary
        
        except Exception as e:
            logger.exception(f'Error generating summary: {e}')
            return self._get_fallback_summary(assessment_data)
    
    def generate_recommendations(self, assessment_data: Dict) -> Optional[List[str]]:
        """
        Generate personalized learning recommendations
        
        Args:
            assessment_data: Dictionary containing assessment results
        
        Returns:
            List of recommendations or None if generation fails
        """
        if not self.model:
            return self._get_fallback_recommendations(assessment_data)
        
        try:
            prompt = self._build_recommendations_prompt(assessment_data)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=400,
                )
            )
            
            # Parse recommendations (expecting a list)
            recommendations_text = response.text.strip()
            recommendations = [
                line.strip().lstrip('•-*').strip() 
                for line in recommendations_text.split('\n') 
                if line.strip() and not line.strip().startswith('#')
            ]
            
            logger.info(f'✅ Generated {len(recommendations)} AI recommendations')
            return recommendations[:5]  # Limit to 5 recommendations
        
        except Exception as e:
            logger.exception(f'Error generating recommendations: {e}')
            return self._get_fallback_recommendations(assessment_data)
    
    def _build_summary_prompt(self, assessment_data: Dict) -> str:
        """Build prompt for summary generation"""
        domain = assessment_data.get('domain', 'cybersecurity')
        score = assessment_data.get('score', 0)
        correct = assessment_data.get('correct_answers', 0)
        total = assessment_data.get('total_questions', 0)
        difficulty = assessment_data.get('difficulty', 'intermediate')
        
        return f"""You are a cybersecurity education expert. Provide a brief, encouraging 2-3 sentence summary of this student's assessment performance.

Domain: {domain.replace('-', ' ').title()}
Score: {score}%
Correct Answers: {correct}/{total}
Difficulty Level: {difficulty.title()}

Keep the tone positive and constructive. Focus on strengths and areas for growth. Be specific about the domain."""
    
    def _build_recommendations_prompt(self, assessment_data: Dict) -> str:
        """Build prompt for recommendations generation"""
        domain = assessment_data.get('domain', 'cybersecurity')
        score = assessment_data.get('score', 0)
        difficulty = assessment_data.get('difficulty', 'intermediate')
        weak_areas = assessment_data.get('weak_areas', [])
        
        weak_areas_text = ', '.join(weak_areas) if weak_areas else 'general concepts'
        
        return f"""You are a cybersecurity education expert. Provide 4-5 specific, actionable learning recommendations for a student.

Domain: {domain.replace('-', ' ').title()}
Score: {score}%
Current Level: {difficulty.title()}
Weak Areas: {weak_areas_text}

Provide practical recommendations like specific courses, certifications, hands-on labs, or resources. 
Return ONLY a bulleted list, one recommendation per line, without additional explanation."""
    
    def _get_fallback_summary(self, assessment_data: Dict) -> str:
        """Generate a basic summary without AI"""
        score = assessment_data.get('score', 0)
        domain = assessment_data.get('domain', 'cybersecurity').replace('-', ' ').title()
        
        if score >= 80:
            return f"Excellent performance in {domain}! You've demonstrated strong understanding of the core concepts. Keep up the great work and consider advancing to more challenging material."
        elif score >= 60:
            return f"Good job on the {domain} assessment! You've shown a solid grasp of the fundamentals. Focus on areas where you struggled to strengthen your knowledge further."
        else:
            return f"Thank you for completing the {domain} assessment. This is a learning opportunity! Review the explanations provided and consider additional study in the areas where you found questions challenging."
    
    def _get_fallback_recommendations(self, assessment_data: Dict) -> List[str]:
        """Generate basic recommendations without AI"""
        domain = assessment_data.get('domain', 'cybersecurity').replace('-', ' ').title()
        score = assessment_data.get('score', 0)
        
        recommendations = [
            f"Review the question explanations to understand the correct answers",
            f"Practice with hands-on labs in {domain}",
            f"Study the learning points provided after each question",
        ]
        
        if score < 60:
            recommendations.append(f"Start with foundational {domain} courses")
            recommendations.append("Join study groups or forums to discuss concepts")
        elif score < 80:
            recommendations.append(f"Pursue intermediate {domain} certifications")
            recommendations.append("Work on real-world projects to apply your knowledge")
        else:
            recommendations.append(f"Consider advanced {domain} certifications")
            recommendations.append("Contribute to open-source security projects")
        
        return recommendations

# Global instance
_gemini_service = None

def get_gemini_service() -> GeminiService:
    """Get the global Gemini service instance"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service

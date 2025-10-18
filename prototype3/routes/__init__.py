"""
Routes package initialization
"""

from .home import home_bp
from .assessment import assessment_bp
from .dashboard import dashboard_bp
from .api import api_bp

__all__ = [
    'home_bp',
    'assessment_bp',
    'dashboard_bp',
    'api_bp',
]

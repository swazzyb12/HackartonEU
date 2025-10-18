"""
Badges (Achievements) service
Defines badge rules and evaluates which badges a user has earned.
"""
from __future__ import annotations

from typing import Dict, Any, List, Callable, Set
from datetime import datetime


def _get_total_assessments(user_stats: Dict[str, Any]) -> int:
    return int(user_stats.get('total_assessments', 0) or 0)


def _get_history(user_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
    return list(user_stats.get('history', []) or [])


def _best_scores_by_domain(history: List[Dict[str, Any]]) -> Dict[str, float]:
    best: Dict[str, float] = {}
    for h in history:
        d = h.get('domain')
        s = float(h.get('score', 0) or 0)
        if d is None:
            continue
        best[d] = max(best.get(d, 0.0), s)
    return best


def _has_completed_all_domains(history: List[Dict[str, Any]], min_score: float = 0) -> bool:
    domains = {h.get('domain') for h in history if h.get('domain')}
    required = {'network-security', 'secure-coding', 'incident-response'}
    if not required.issubset(domains):
        return False
    if min_score > 0:
        by_domain_best = _best_scores_by_domain(history)
        return all(by_domain_best.get(d, 0) >= min_score for d in required)
    return True


def _last_two_scores(history: List[Dict[str, Any]]) -> List[float]:
    if len(history) < 2:
        return []
    sorted_hist = sorted(history, key=lambda x: x.get('date', ''))
    return [float(sorted_hist[-2].get('score', 0) or 0), float(sorted_hist[-1].get('score', 0) or 0)]


def _consecutive_assessments(history: List[Dict[str, Any]]) -> int:
    # Simple consecutive count of assessments taken (we count all as consecutive since no gaps logic)
    return len(history)


BadgeCheck = Callable[[Dict[str, Any], Dict[str, Any]], bool]


def _check_first_assessment(user_stats: Dict[str, Any], results: Dict[str, Any]) -> bool:
    return _get_total_assessments(user_stats) >= 1


def _check_expert(user_stats: Dict[str, Any], results: Dict[str, Any]) -> bool:
    return float(results.get('score', 0) or 0) >= 90.0


def _check_perfect(user_stats: Dict[str, Any], results: Dict[str, Any]) -> bool:
    return float(results.get('score', 0) or 0) >= 100.0


def _check_consistent(user_stats: Dict[str, Any], results: Dict[str, Any]) -> bool:
    return _get_total_assessments(user_stats) >= 5


def _check_ironman(user_stats: Dict[str, Any], results: Dict[str, Any]) -> bool:
    return _get_total_assessments(user_stats) >= 10


def _check_marathon(user_stats: Dict[str, Any], results: Dict[str, Any]) -> bool:
    return _get_total_assessments(user_stats) >= 25


def _check_speedster(user_stats: Dict[str, Any], results: Dict[str, Any]) -> bool:
    # Average time per question at or below 20 seconds
    return float(results.get('avg_time_per_question', 9999)) <= 20.0


def _check_all_rounder(user_stats: Dict[str, Any], results: Dict[str, Any]) -> bool:
    return _has_completed_all_domains(_get_history(user_stats))


def _check_master(user_stats: Dict[str, Any], results: Dict[str, Any]) -> bool:
    # 80%+ in all three domains at least once
    return _has_completed_all_domains(_get_history(user_stats), min_score=80)


def _check_domain_proficiency(domain: str, threshold: float) -> BadgeCheck:
    def _inner(user_stats: Dict[str, Any], results: Dict[str, Any]) -> bool:
        best = _best_scores_by_domain(_get_history(user_stats))
        return float(best.get(domain, 0)) >= threshold
    return _inner


def _check_comeback(user_stats: Dict[str, Any], results: Dict[str, Any]) -> bool:
    # Improve at least 20 points over previous assessment
    last_two = _last_two_scores(_get_history(user_stats))
    if len(last_two) != 2:
        return False
    prev, curr = last_two
    return (curr - prev) >= 20.0


BADGE_DEFS: List[Dict[str, Any]] = [
    {
        'id': 'first_assessment',
        'name': 'First Steps',
        'description': 'Complete your first assessment',
        'icon': '🎯',
        'check': _check_first_assessment,
    },
    {
        'id': 'expert',
        'name': 'Expert Level',
        'description': 'Score 90% or higher on an assessment',
        'icon': '⭐',
        'check': _check_expert,
    },
    {
        'id': 'perfect',
        'name': 'Perfect Score',
        'description': 'Score 100% on an assessment',
        'icon': '🏆',
        'check': _check_perfect,
    },
    {
        'id': 'consistent',
        'name': 'Consistent Learner',
        'description': 'Complete 5 assessments',
        'icon': '📚',
        'check': _check_consistent,
    },
    {
        'id': 'ironman',
        'name': 'Iron Learner',
        'description': 'Complete 10 assessments',
        'icon': '💪',
        'check': _check_ironman,
    },
    {
        'id': 'marathon',
        'name': 'Marathon Mind',
        'description': 'Complete 25 assessments',
        'icon': '🏃',
        'check': _check_marathon,
    },
    {
        'id': 'speedster',
        'name': 'Speedster',
        'description': 'Average ≤ 20s per question in an assessment',
        'icon': '⚡',
        'check': _check_speedster,
    },
    {
        'id': 'all_rounder',
        'name': 'All-Rounder',
        'description': 'Complete assessments in all three domains',
        'icon': '🧭',
        'check': _check_all_rounder,
    },
    {
        'id': 'master',
        'name': 'Master of All',
        'description': 'Score 80%+ in all three domains',
        'icon': '👑',
        'check': _check_master,
    },
    # Domain proficiency badges
    {
        'id': 'net_secure_pro',
        'name': 'Network Guardian',
        'description': 'Score 80%+ in Network Security',
        'icon': '🛡️',
        'check': _check_domain_proficiency('network-security', 80),
    },
    {
        'id': 'secure_code_pro',
        'name': 'Code Defender',
        'description': 'Score 80%+ in Secure Coding',
        'icon': '💻',
        'check': _check_domain_proficiency('secure-coding', 80),
    },
    {
        'id': 'ir_pro',
        'name': 'Incident Responder',
        'description': 'Score 80%+ in Incident Response',
        'icon': '🚨',
        'check': _check_domain_proficiency('incident-response', 80),
    },
    {
        'id': 'comeback',
        'name': 'Comeback Kid',
        'description': 'Improve your score by 20+ points over last time',
        'icon': '🔁',
        'check': _check_comeback,
    },
]


def evaluate_badges(user_stats: Dict[str, Any], last_results: Dict[str, Any]) -> List[str]:
    """
    Return a list of newly earned badge ids based on current user_stats and the
    most recent assessment results.
    """
    already: Set[str] = set(user_stats.get('badges', []) or [])
    newly_earned: List[str] = []

    for b in BADGE_DEFS:
        bid = b['id']
        try:
            if bid not in already and b['check'](user_stats, last_results):
                newly_earned.append(bid)
        except Exception:
            # Be robust: a failing check shouldn't break badge awarding
            continue
    return newly_earned


def all_badges_with_earned(user_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
    earned: Set[str] = set(user_stats.get('badges', []) or [])
    result: List[Dict[str, Any]] = []
    for b in BADGE_DEFS:
        result.append({
            'id': b['id'],
            'name': b['name'],
            'description': b['description'],
            'icon': b['icon'],
            'earned': b['id'] in earned,
        })
    return result

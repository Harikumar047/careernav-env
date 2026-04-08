def grade_skill_gap(expected_gaps, flagged_gaps):
    """Task 1 Grader: F1 Score."""
    expected = set(expected_gaps)
    flagged = set(flagged_gaps)
    tp = len(expected.intersection(flagged))
    fp = len(flagged - expected)
    fn = len(expected - flagged)
    if tp == 0: return 0.0
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    return 2 * (precision * recall) / (precision + recall)

def grade_course_recommender(recommended_courses, gaps_remaining, initial_gaps, budget_used, budget_total):
    coverage = (initial_gaps - len(gaps_remaining)) / max(initial_gaps, 1)
    budget_ratio = min(budget_used / max(budget_total, 1), 1.0)
    overrun_penalty = max(0, budget_ratio - 1.0) * 0.5
    return round(max(0.0, min(1.0, coverage - overrun_penalty)), 3)

def grade_full_optimizer(match_score, bias_detected, prereq_violations, market_drifted, gaps_closed, initial_gaps):
    coverage = gaps_closed / max(initial_gaps, 1)
    bias_score = 0.0 if bias_detected else 1.0
    prereq_score = max(0.0, 1.0 - prereq_violations * 0.15)
    drift_score = 1.0 if market_drifted else 0.7
    return round(0.30 * coverage + 0.25 * match_score + 0.20 * bias_score + 0.15 * prereq_score + 0.10 * drift_score, 3)

def grade_scheme_matcher(schemes_matched, schemes_available, wrong_schemes):
    if not schemes_available:
        return 0.0
    precision = len(schemes_matched) / max(len(schemes_matched) + wrong_schemes, 1)
    recall = len(schemes_matched) / max(len(schemes_available), 1)
    if precision + recall == 0:
        return 0.0
    return round(2 * precision * recall / (precision + recall), 3)

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

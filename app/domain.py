"""Deterministic bootstrap and interpretable canary guardrails."""
import random
from statistics import mean

def percentile(values, q):
    ordered = sorted(values)
    position = (len(ordered)-1)*q
    lower = int(position)
    upper = min(lower+1, len(ordered)-1)
    return ordered[lower] + (ordered[upper]-ordered[lower])*(position-lower)

def assess(baseline, candidate, max_regression=0.15, iterations=1000):
    if min(len(baseline), len(candidate)) < 20:
        return {'decision': 'insufficient_data', 'reason': 'At least 20 samples per cohort required', 'model': 'bootstrap-mean-v1'}
    rng = random.Random(42)
    reference = mean(baseline)
    if reference <= 0:
        return {'decision': 'insufficient_data', 'reason': 'Baseline mean must be positive', 'model': 'bootstrap-mean-v1'}
    deltas = []
    for _ in range(iterations):
        b = mean(rng.choices(baseline, k=len(baseline)))
        c = mean(rng.choices(candidate, k=len(candidate)))
        deltas.append((c-b)/max(b, 1e-9))
    low, high = percentile(deltas, 0.025), percentile(deltas, 0.975)
    decision = 'rollback' if low > max_regression else 'promote' if high <= max_regression else 'hold'
    return {'decision': decision, 'mean_regression': (mean(candidate)-reference)/reference,
            'ci95': [low, high], 'threshold': max_regression,
            'baseline_p95': percentile(baseline, 0.95), 'candidate_p95': percentile(candidate, 0.95),
            'model': 'bootstrap-mean-v1', 'iterations': iterations, 'seed': 42,
            'reason': 'Confidence interval compared with allowed mean latency regression'}

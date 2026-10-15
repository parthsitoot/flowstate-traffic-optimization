"""One-second queue simulator with identical traffic for each policy.

Forecasts use only completed arrival intervals. History records the signal that
actually applied during that second, even when a switch is scheduled afterward.
"""
from collections import deque
import numpy as np

DIRECTIONS = ['North', 'East', 'South', 'West']
SCENARIOS = {'balanced': [.16, .16, .16, .16], 'rush': [.36, .08, .30, .06], 'surge': [.10, .12, .10, .12]}
MIN_GREEN = 10
MAX_GREEN = 45
FIXED_GREEN = 25
CLEARANCE = 3
OVERDUE = 90
FORECAST_WEIGHT = .7
AGE_WEIGHT = .08
SWITCH_MARGIN = 2


def arrivals_for(scenario, seed, seconds):
    rng = np.random.default_rng(seed)
    rates = np.tile(SCENARIOS[scenario], (seconds, 1))
    if scenario == 'surge':
        rates[seconds // 3:2 * seconds // 3, 1] = .65
    return rng.poisson(rates)


def simulate(arrivals, model=None, adaptive=False, sample_every=2):
    """Run a controller; sample_every=1 exposes each second for verification."""
    arrivals = np.asarray(arrivals)
    if (arrivals.ndim != 2 or arrivals.shape[1] != 4 or not len(arrivals)
            or not np.all(np.isfinite(arrivals)) or np.any(arrivals < 0)
            or np.any(arrivals != np.floor(arrivals))):
        raise ValueError('Arrivals must be a nonempty array of nonnegative integer counts with four columns.')
    if not isinstance(sample_every, int) or sample_every < 1:
        raise ValueError('sample_every must be a positive integer.')
    queues = [deque() for _ in DIRECTIONS]
    phase, next_phase, clearance_left, green_age = 0, 0, 0, 0
    since_green = [0] * 4
    departed_waits, history = [], []
    total_queue = switches = peak_queue = 0
    predictions = [0.] * 4

    for t, incoming in enumerate(arrivals):
        for d in range(4):
            queues[d].extend([t] * int(incoming[d]))
            since_green[d] += 1

        if t % 10 == 0 and model is not None:
            features = [[int(arrivals[max(0, t - 10 * (k + 1)):max(0, t - 10 * k), d].sum())
                         for k in range(3)] for d in range(4)]
            predictions = model.predict(features).tolist()

        # Save the phase in force BEFORE scheduling the next second's state.
        displayed_phase = phase
        in_clearance = clearance_left > 0
        if in_clearance:
            clearance_left -= 1
            if clearance_left == 0:
                phase, green_age = next_phase, 0
        else:
            since_green[phase] = 0
            if queues[phase]:
                departed_waits.append(t - queues[phase].popleft())
            green_age += 1
            if adaptive:
                scores = [len(queues[d]) + FORECAST_WEIGHT * predictions[d] + AGE_WEIGHT * since_green[d]
                          for d in range(4)]
                overdue = [d for d in range(4) if queues[d] and since_green[d] >= OVERDUE and d != phase]
                candidate = (max(overdue, key=lambda d: since_green[d]) if overdue
                             else max(range(4), key=lambda d: scores[d]))
                change = green_age >= MIN_GREEN and (
                    bool(overdue) or (candidate != phase and scores[candidate] > scores[phase] + SWITCH_MARGIN)
                    or green_age >= MAX_GREEN)
                if green_age >= MAX_GREEN and candidate == phase:
                    candidate = max((d for d in range(4) if d != phase), key=lambda d: scores[d])
            else:
                candidate, change = (phase + 1) % 4, green_age >= FIXED_GREEN
            if change:
                next_phase, clearance_left = candidate, CLEARANCE
                switches += 1

        queue_counts = list(map(len, queues))
        total_queue += sum(queue_counts)
        peak_queue = max(peak_queue, sum(queue_counts))
        if t % sample_every == 0 or t == len(arrivals) - 1:
            history.append({'time': t + 1, 'queues': queue_counts, 'phase': displayed_phase,
                            'amber': in_clearance, 'served': len(departed_waits),
                            'queue_seconds': total_queue, 'forecast': [round(x, 1) for x in predictions]})

    generated = int(arrivals.sum())
    return {'history': history, 'metrics': {
        'arrivals': generated, 'served': len(departed_waits), 'remaining': sum(map(len, queues)),
        'delay_per_arrival': round(total_queue / max(generated, 1), 2),
        'mean_departed_wait': round(float(np.mean(departed_waits)) if departed_waits else 0, 2),
        'queue_seconds': total_queue, 'switches': switches, 'peak_queue': peak_queue}}


def compare(model, scenario='rush', seed=42, seconds=600):
    arrivals = arrivals_for(scenario, seed, seconds)
    fixed = simulate(arrivals)
    smart = simulate(arrivals, model, True)
    reactive = simulate(arrivals, None, True)
    base = fixed['metrics']['queue_seconds']
    return {'scenario': scenario, 'seed': seed, 'seconds': seconds, 'fixed': fixed, 'smart': smart,
            'reactive': reactive, 'improvement': round(100 * (base - smart['metrics']['queue_seconds']) / max(base, 1), 1)}

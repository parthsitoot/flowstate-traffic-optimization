"""Shared API logic used by both localhost and Vercel's Python functions.

The cached bundle fits three real estimators per process on the same split.
Warm requests reuse them. No fitted model is accepted from users.
"""
from functools import lru_cache
from threading import Lock
from .model import train_models
from .simulation import compare, simulate, arrivals_for, SCENARIOS
from .vision import analyze

_training_lock = Lock()

@lru_cache(maxsize=1)
def _train_once():
    return train_models()

def comparison_bundle():
    with _training_lock:
        return _train_once()

def model_bundle():
    return comparison_bundle()['primary']

def response_for(endpoint, query):
    """Return (HTTP status, JSON-compatible data); query values are lists."""
    try:
        if endpoint == 'model':
            bundle = comparison_bundle()
            return 200, {**bundle['primary'][1], 'model_comparison': bundle['scores']}
        if endpoint == 'predict':
            raw = query.get('counts', [''])[0].split(',')
            if len(raw) != 3:
                return 400, {'error': 'Enter exactly three arrival counts, newest first.'}
            try:
                counts = [int(value) for value in raw]
            except (ValueError, TypeError):
                return 400, {'error': 'Arrival counts must be whole numbers from 0 to 100.'}
            if any(value < 0 or value > 100 for value in counts):
                return 400, {'error': 'Arrival counts must be whole numbers from 0 to 100.'}
            model, metrics = model_bundle()
            prediction = float(model.predict([counts])[0])
            unusual = any(value > maximum for value, maximum in zip(counts, metrics['feature_maxima']))
            bundle = comparison_bundle()
            predictions = [{**score, 'prediction': round(float(
                bundle['estimators'][score['id']].predict([counts])[0]), 3)}
                for score in bundle['scores']]
            return 200, {
                'inputs': counts, 'prediction': round(prediction, 3),
                'rounded_prediction': round(prediction), 'horizon_seconds': 10,
                'model_type': metrics['model_type'], 'n_estimators': metrics['n_estimators'],
                'test_mae': metrics['mae'], 'outside_training_range': unusual,
                'models': predictions,
                'note': ('Some counts exceed the observed training range; this forecast may be unreliable.'
                         if unusual else 'Expected arrivals, not a guaranteed count. Trained on synthetic traffic.')}
        if endpoint == 'run':
            scenario = query.get('scenario', ['rush'])[0]
            seed = int(query.get('seed', ['42'])[0])
            if scenario not in SCENARIOS or not 0 <= seed <= 999999:
                raise ValueError('Choose a valid scenario and a seed from 0 to 999999.')
            bundle = comparison_bundle()
            result = compare(bundle['primary'][0], scenario, seed)
            # All estimators receive identical arrival matrices and controller rules.
            arrivals = arrivals_for(scenario, seed, result['seconds'])
            outputs = []
            for score in bundle['scores']:
                run = (result['smart'] if score['id'] == 'random_forest' else
                       simulate(arrivals, bundle['estimators'][score['id']], True))
                outputs.append({**score, 'metrics': run['metrics']})
            result['model_comparison'] = outputs
            return 200, result
        if endpoint == 'vision':
            queues = [int(x) for x in query.get('q', ['0,0,0,0'])[0].split(',')]
            if len(queues) != 4 or any(x < 0 or x > 10000 for x in queues):
                raise ValueError('Provide four queue counts from 0 to 10000.')
            return 200, analyze(queues)
        return 404, {'error': 'Unknown API endpoint.'}
    except (ValueError, IndexError, TypeError):
        return 400, {'error': 'Invalid request parameters.'}

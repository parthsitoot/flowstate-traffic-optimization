"""Shared API logic used by both localhost and Vercel's Python functions.

The cached bundle trains one real Random Forest per process. Warm requests reuse
it; cold serverless processes train again. No fitted model is accepted from users.
"""
from functools import lru_cache
from threading import Lock
from .model import train
from .simulation import compare, SCENARIOS
from .vision import analyze

_training_lock = Lock()

@lru_cache(maxsize=1)
def _train_once():
    return train()

def model_bundle():
    with _training_lock:
        return _train_once()

def response_for(endpoint, query):
    """Return (HTTP status, JSON-compatible data); query values are lists."""
    try:
        if endpoint == 'model':
            return 200, model_bundle()[1]
        if endpoint == 'run':
            scenario = query.get('scenario', ['rush'])[0]
            seed = int(query.get('seed', ['42'])[0])
            if scenario not in SCENARIOS or not 0 <= seed <= 999999:
                raise ValueError('Choose a valid scenario and a seed from 0 to 999999.')
            return 200, compare(model_bundle()[0], scenario, seed)
        if endpoint == 'vision':
            queues = [int(x) for x in query.get('q', ['0,0,0,0'])[0].split(',')]
            if len(queues) != 4 or any(x < 0 or x > 10000 for x in queues):
                raise ValueError('Provide four queue counts from 0 to 10000.')
            return 200, analyze(queues)
        return 404, {'error': 'Unknown API endpoint.'}
    except (ValueError, IndexError, TypeError):
        return 400, {'error': 'Invalid request parameters.'}

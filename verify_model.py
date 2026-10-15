"""Verify the trained model's predictions and its actual role in signal control.
Run: python3 verify_model.py
"""
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import mean_absolute_error
from sklearn.utils.validation import check_is_fitted
from src.model import train, dataset
from src.simulation import compare


def verify():
    model, metrics = train()
    check_is_fitted(model)
    x_test, y_test = dataset(722, 100)
    _, y_train = dataset(21, 300)
    inputs = [[0,0,0], [1,1,1], [3,3,3], [6,6,6], [10,10,10]]
    predictions = model.predict(inputs)
    assert np.all(np.isfinite(predictions)) and np.all(predictions >= 0)
    assert np.all(np.diff(predictions) > 0), 'Steady higher demand should give a higher forecast in these examples.'
    baselines = {
        'random_forest': metrics['mae'],
        'last_count_persistence': metrics['persistence_mae'],
        'three_window_average': float(mean_absolute_error(y_test, x_test.mean(axis=1))),
        'training_mean_constant': float(mean_absolute_error(y_test, np.full(len(y_test), y_train.mean()))),
    }
    assert baselines['random_forest'] < min(v for k,v in baselines.items() if k != 'random_forest')
    run = compare(model, 'rush', 42)
    learned = run['smart']['history']
    reactive = run['reactive']['history']
    different = sum((a['phase'],a['amber']) != (b['phase'],b['amber']) for a,b in zip(learned,reactive))
    assert different > 0, 'The learned forecast should actually influence this controller run.'
    report = {
        'status': 'PASS', 'model': type(model).__name__, 'fitted_trees': len(model.estimators_),
        'test_samples': len(y_test), 'heldout_mae_vehicles_per_10_seconds': baselines,
        'example_predictions': [{'recent_10s_counts_newest_first': x, 'predicted_next_10s_arrivals': round(float(y),3)} for x,y in zip(inputs,predictions)],
        'controller_integration': {'scenario':'rush','seed':42,'sampled_signal_states_changed_by_forecast':different,
            'ml_delay_per_arrival':run['smart']['metrics']['delay_per_arrival'],
            'queue_only_delay_per_arrival':run['reactive']['metrics']['delay_per_arrival'],
            'fixed_delay_per_arrival':run['fixed']['metrics']['delay_per_arrival']},
        'interpretation': 'Forecasts are expected counts and can be fractional. Zero recent traffic can still predict future arrivals. Synthetic held-out data only. ML is slightly worse than queue-only on this specific seed; multi-seed results are in evaluation_summary.json.'
    }
    path = Path(__file__).parent/'artifacts/model_verification.json'
    path.write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    return report

if __name__ == '__main__': verify()

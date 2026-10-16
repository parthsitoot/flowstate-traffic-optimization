"""Compare the deployed forest with two trained alternatives on identical data.

Run: python3 compare_models.py
This evaluates forecasting only; it does not change the deployed controller.
"""
import csv
import json
from pathlib import Path

import numpy as np
import sklearn
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.model import FEATURES, dataset, train_models


def compare_models():
    x_train, y_train = dataset(21, 300)
    x_test, y_test = dataset(722, 100)
    bundle = train_models()
    models = [(row['name'], bundle['estimators'][row['id']])
              for row in bundle['scores']]

    rows = []
    for name, model in models:
        predictions = model.predict(x_test)
        if predictions.shape != y_test.shape or not np.isfinite(predictions).all():
            raise ValueError(f'{name} returned invalid predictions.')
        rows.append({
            'model': name,
            'mae': float(mean_absolute_error(y_test, predictions)),
            'rmse': float(mean_squared_error(y_test, predictions) ** 0.5),
            'parameters': model.get_params(),
        })

    report = {
        'dataset': 'Synthetic Poisson counts with changing arrival rates',
        'features_newest_first': FEATURES,
        'training_episodes': 300, 'training_seed': 21,
        'training_rows': len(y_train),
        'test_episodes': 100, 'test_seed': 722, 'test_rows': len(y_test),
        'numpy_version': np.__version__, 'sklearn_version': sklearn.__version__,
        'evaluation': 'Same independent episode split and features for every model. '
                      'No parameter search; single test split; no statistical significance claim.',
        'models': rows,
        'lowest_mae': min(rows, key=lambda r: r['mae'])['model'],
        'lowest_rmse': min(rows, key=lambda r: r['rmse'])['model'],
        'interpretation': 'Random Forest is the implemented forecasting model, '
                          'not a universally best algorithm. Report every comparator, '
                          'including models that outperform it on a metric. '
                          'Forecast errors do not establish signal waiting-time gains.',
    }
    output = Path(__file__).resolve().parent / 'artifacts'
    output.mkdir(exist_ok=True)
    (output / 'algorithm_comparison.json').write_text(json.dumps(report, indent=2) + '\n')
    with (output / 'algorithm_comparison.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['model', 'mae', 'rmse'])
        writer.writeheader()
        writer.writerows({k: r[k] for k in writer.fieldnames} for r in rows)
    return report


if __name__ == '__main__':
    result = compare_models()
    for row in result['models']:
        print(f"{row['model']:18s} MAE={row['mae']:.6f}  RMSE={row['rmse']:.6f}")
    print(f"Lowest MAE: {result['lowest_mae']}; lowest RMSE: {result['lowest_rmse']}")

"""Train an arrival forecast on synthetic, independent traffic episodes."""
import json
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ['arrivals_last_10s', 'arrivals_previous_10s', 'arrivals_previous_20_to_30s']

def dataset(seed, episodes):
    rng = np.random.default_rng(seed)
    X, y = [], []
    for _ in range(episodes):
        rate = rng.uniform(.04, .65)
        counts = []
        for t in range(36):
            if t % 6 == 0:
                rate = np.clip(rate + rng.normal(0, .09), .03, .7)
            counts.append(rng.poisson(rate * 10))
        for i in range(3, len(counts)):
            X.append(counts[i-3:i][::-1])
            y.append(counts[i])
    return np.array(X), np.array(y)

def train():
    X, y = dataset(21, 300)
    xt, yt = dataset(722, 100)  # Entirely separate episodes, never overlapping windows.
    model = RandomForestRegressor(n_estimators=60, max_depth=8, min_samples_leaf=15, random_state=9, n_jobs=1)
    model.fit(X, y)
    p = model.predict(xt)
    metrics = {'training_samples': len(y), 'test_samples': len(yt), 'mae': float(mean_absolute_error(yt, p)),
               'rmse': float(mean_squared_error(yt, p)**.5), 'persistence_mae': float(mean_absolute_error(yt, xt[:,0])),
               'moving_average_mae': float(mean_absolute_error(yt, xt.mean(axis=1))),
               'constant_mae': float(mean_absolute_error(yt, np.full(len(yt), y.mean()))),
               'model_type': 'RandomForestRegressor', 'n_estimators': len(model.estimators_),
               'feature_maxima': X.max(axis=0).astype(int).tolist(),
               'features': FEATURES, 'feature_importances': model.feature_importances_.tolist(),
               'target': 'Vehicle arrivals in the next 10 seconds', 'data': 'Synthetic Poisson arrivals with changing rates; split by independent episode.'}
    return model, metrics


def train_models():
    """Fit all comparators on the same split; keep the forest as the controller model."""
    forest, metrics = train()
    X, y = dataset(21, 300)
    xt, yt = dataset(722, 100)
    definitions = [
        ('random_forest', 'Random Forest', forest,
         'Averages 60 trees. Used by the main signal simulation.'),
        ('linear_regression', 'Linear Regression', LinearRegression(),
         'Learns a weighted combination of the three recent counts.'),
        ('decision_tree', 'Decision Tree', DecisionTreeRegressor(
            max_depth=8, min_samples_leaf=15, random_state=9),
         'One tree, with the same depth and leaf limits as the forest.'),
    ]
    estimators, scores = {}, []
    for key, name, estimator, description in definitions:
        if key != 'random_forest':
            estimator.fit(X, y)
        predicted = estimator.predict(xt)
        estimators[key] = estimator
        scores.append({
            'id': key, 'name': name, 'description': description,
            'mae': float(mean_absolute_error(yt, predicted)),
            'rmse': float(mean_squared_error(yt, predicted) ** .5),
        })
    return {'primary': (forest, metrics), 'estimators': estimators, 'scores': scores}

if __name__ == '__main__':
    _, metrics = train()
    (ROOT/'artifacts').mkdir(exist_ok=True)
    (ROOT/'artifacts/model_metrics.json').write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))

"""Train an arrival forecast on synthetic, independent traffic episodes."""
import json
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestRegressor
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
               'features': FEATURES, 'feature_importances': model.feature_importances_.tolist(),
               'target': 'Vehicle arrivals in the next 10 seconds', 'data': 'Synthetic Poisson arrivals with changing rates; split by independent episode.'}
    return model, metrics

if __name__ == '__main__':
    _, metrics = train()
    (ROOT/'artifacts').mkdir(exist_ok=True)
    (ROOT/'artifacts/model_metrics.json').write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))

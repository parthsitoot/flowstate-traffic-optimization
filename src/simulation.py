"""One-second queue simulator. Both policies receive the exact same arrivals."""
import numpy as np
DIRECTIONS = ['North', 'East', 'South', 'West']
SCENARIOS = {'balanced': [.16,.16,.16,.16], 'rush': [.36,.08,.30,.06], 'surge': [.10,.12,.10,.12]}

def arrivals_for(scenario, seed, seconds):
    rng = np.random.default_rng(seed)
    rates = np.tile(SCENARIOS[scenario], (seconds,1))
    if scenario == 'surge':
        rates[seconds//3:2*seconds//3,1] = .65
    return rng.poisson(rates)

def simulate(arrivals, model=None, adaptive=False):
    queues = [[],[],[],[]]
    phase, next_phase, amber, green_age = 0, 0, 0, 0
    since_green = [0,0,0,0]
    departed_waits, history, total_queue, switches = [], [], 0, 0
    predictions = [0.,0.,0.,0.]
    for t, incoming in enumerate(arrivals):
        for d in range(4):
            queues[d].extend([t]*int(incoming[d]))
            since_green[d] += 1
        if t % 10 == 0 and model is not None:
            features = [[int(arrivals[max(0,t-10*(k+1)):max(0,t-10*k), d].sum()) for k in range(3)] for d in range(4)]
            predictions = model.predict(features).tolist()
        if amber:
            amber -= 1
            if amber == 0:
                phase, green_age = next_phase, 0
        else:
            since_green[phase] = 0
            # Discharge one vehicle/second. Single approach green; no turning conflicts.
            if queues[phase]:
                departed_waits.append(t - queues[phase].pop(0))
            green_age += 1
            if adaptive:
                score = [len(queues[d]) + .7*predictions[d] + .08*since_green[d] for d in range(4)]
                overdue = [d for d in range(4) if queues[d] and since_green[d] >= 90 and d != phase]
                candidate = max(overdue, key=lambda d: since_green[d]) if overdue else max(range(4), key=lambda d: score[d])
                change = green_age >= 10 and (bool(overdue) or (candidate != phase and score[candidate] > score[phase]+2) or green_age >= 45)
                if green_age >= 45 and candidate == phase:
                    candidate = max((d for d in range(4) if d != phase), key=lambda d: score[d])
            else:
                candidate, change = (phase+1)%4, green_age >= 25
            if change:
                next_phase, amber = candidate, 3
                switches += 1
        total_queue += sum(map(len,queues))
        if t % 2 == 0 or t == len(arrivals)-1:
            history.append({'time':t+1, 'queues':list(map(len,queues)), 'phase':phase, 'amber':bool(amber),
                            'served':len(departed_waits), 'queue_seconds':total_queue, 'forecast':[round(x,1) for x in predictions]})
    generated = int(arrivals.sum())
    return {'history':history, 'metrics':{'arrivals':generated, 'served':len(departed_waits), 'remaining':sum(map(len,queues)),
         'delay_per_arrival':round(total_queue/max(generated,1),2), 'mean_departed_wait':round(float(np.mean(departed_waits)) if departed_waits else 0,2),
         'queue_seconds':total_queue, 'switches':switches, 'peak_queue':max(sum(h['queues']) for h in history)}}

def compare(model, scenario='rush', seed=42, seconds=600):
    arrivals = arrivals_for(scenario, seed, seconds)
    fixed = simulate(arrivals)
    smart = simulate(arrivals, model, True)
    reactive = simulate(arrivals, None, True)
    base = fixed['metrics']['queue_seconds']
    return {'scenario':scenario, 'seed':seed, 'seconds':seconds, 'fixed':fixed, 'smart':smart, 'reactive':reactive,
            'improvement':round(100*(base-smart['metrics']['queue_seconds'])/max(base,1),1)}

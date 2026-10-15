"""Reproducible multi-seed evaluation. No cherry-picked seed selection."""
import csv,json
from pathlib import Path
from statistics import mean,stdev
from src.model import train
from src.simulation import compare,SCENARIOS
root=Path(__file__).parent/'artifacts';root.mkdir(exist_ok=True)
model,metrics=train();(root/'model_metrics.json').write_text(json.dumps(metrics,indent=2))
rows=[]
for scenario in SCENARIOS:
    for seed in range(10):
        result=compare(model,scenario,seed)
        for policy in ('fixed','reactive','smart'):
            rows.append({'scenario':scenario,'seed':seed,'policy':policy,**result[policy]['metrics']})
with (root/'evaluation.csv').open('w') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
summary={}
for scenario in SCENARIOS:
    summary[scenario]={}
    for policy in ('fixed','reactive','smart'):
        r=[x for x in rows if x['scenario']==scenario and x['policy']==policy]
        vals=[x['delay_per_arrival'] for x in r]
        summary[scenario][policy]={'mean_delay':round(mean(vals),2),'sd_delay':round(stdev(vals),2),'mean_served':round(mean(x['served'] for x in r),1)}
(root/'evaluation_summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))

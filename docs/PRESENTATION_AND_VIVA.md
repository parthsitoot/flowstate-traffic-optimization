# Presentation and viva guide

## 5-minute script

**0:00–0:40 — Problem and objective**
“My project is Smart Traffic Signal Optimization Using Machine Learning and Computer Vision. The problem is that equal fixed timers do not respond to uneven traffic. My objective is to build a reproducible prototype that predicts short-term traffic demand and uses it to prioritize signals.”

**0:40–1:25 — System**
“There are three components. Computer vision demonstrates vehicle counting from synthetic images. A random forest predicts arrivals in the next ten seconds. A priority controller combines queue length, predicted arrivals, and waiting age. In this prototype the simulator supplies the full counts to the controller; camera processing is a separate demonstration.”

**1:25–2:10 — Machine learning**
“The input features are arrivals in the three previous ten-second intervals. The target is arrivals in the next interval. I trained on 9,900 windows and tested on 3,300 windows from separate episodes. The forest's MAE is 1.70 vehicles, compared with 2.06 for repeating the last observed count. Keeping episodes separate avoids leakage between train and test windows.”

**2:10–3:20 — Live demo**
Open Intersection overview. Select Morning rush, seed 42, Run experiment. Show the simulated intersection. Pause and scrub the timeline. Point to the synthetic detection boxes. Explain that the headline metrics describe the entire 600-second experiment while playback shows individual moments. Show the queue chart and the three-policy table under Model & methodology.

**3:20–4:15 — Results**
“Evaluation uses three scenarios and ten seeds each. All policies receive identical arrivals for each seed. Rush-scenario average delay is 99.39 seconds for fixed signals, 51.29 for queue-only adaptation, and 49.10 with ML. Adaptive control supplies most of the benefit; forecasting contributes a smaller additional gain.”

**4:15–5:00 — Limitations and conclusion**
“This is a simulation, not a field deployment. It excludes pedestrian crossings, turns, travel time, and real video detection. The next step is to connect a trained detector and tracker to a calibrated traffic simulator. The project demonstrates supervised forecasting, image processing, and fair controller evaluation.”

## Common viva questions

**Why random forest?** It handles nonlinear count relationships, is fast on small tabular datasets, and requires little feature scaling. It is a practical choice, not proof it is the best model.

**Classification or regression?** Regression. We predict a numeric arrival count.

**What dataset did you use?** Synthetic Poisson arrival episodes with changing rates. Training uses seed 21; held-out episodes use seed 722. Controller evaluation uses seeds 0–9 for each scenario.

**Where is computer vision?** `src/vision.py`: thresholding pixels by color, grouping connected pixels, filtering small components, assigning detections to approach regions, and drawing boxes in the dashboard.

**Does the camera feed control the signal?** Not yet. The camera demonstrates detection independently. Complete queue and arrival counts come from the simulator. Integrating tracking and calibrated arrival estimation is future work.

**Why not call this reinforcement learning?** There is no learned action policy or reward optimization. Supervised learning predicts demand; explicit rules choose signals.

**How did you avoid data leakage?** Split by complete independent synthetic episodes, not randomly by neighboring time windows. In simulation, forecast features use only completed prior seconds, never future arrival values.

**Why use a queue-only baseline?** It distinguishes the benefit of adaptation from the extra benefit of ML forecasting.

**Why might ML lose on some seeds?** Counts are noisy, the forecaster is imperfect, and the heuristic may react poorly to a particular forecast. Report repeated trials rather than choosing only favorable runs.

**What prevents starvation?** Waiting approaches get age priority and special overdue handling after 90 seconds without green. The current green has a maximum duration. This is not a formal bound on individual vehicle waiting time.

**Can this control real lights?** No. It needs road data, detection validation, calibrated discharge rates, pedestrian and turning phases, fault handling, and traffic engineering safety review.

**Why not measure only served vehicles' average wait?** It can omit long-waiting vehicles left in the queue. Our main metric includes waiting accumulated by all arrivals within the experiment window.

**What are the weights 0.7 and 0.08?** Fixed design choices in the heuristic; they are not learned or exhaustively optimized. Weight sensitivity analysis is future work.

**What can you improve next?** Real video with trained vehicle detection and tracking; spatial queue estimates; SUMO-style calibrated simulation; tuning on validation scenarios; confidence intervals and more seeds; pedestrian and emergency phases.

## Before leaving for class

- Charge the laptop and test without internet.
- Run `python3 app.py`, keep the terminal open, and open http://localhost:8000.
- Open Presentation mode and test arrow keys.
- Keep `artifacts/evaluation_summary.json` and `docs/REPORT.md` available if asked for evidence.
- Avoid claiming the generated dataset or footage was collected from real streets.
- Customize your name, institution, and course details before submitting.

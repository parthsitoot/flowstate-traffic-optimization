# Smart Traffic Signal Optimization Using Machine Learning and Computer Vision

**Implementation name:** FlowState  
**Type:** ML course prototype  
**Author:** [Add your name]  
**Institution/course:** [Add your details]

## Abstract

This project investigates adaptive control of a simulated four-way intersection using supervised short-term demand forecasting. A random forest predicts vehicle arrivals over the next ten seconds. A heuristic controller combines these predictions with observed queue size and elapsed time since green. Fixed-time and queue-only adaptive policies provide comparison baselines. A separate classical computer vision module counts vehicles from generated images using color segmentation and connected components. Evaluation covers three synthetic demand scenarios and ten random seeds per scenario. Results demonstrate lower accumulated delay for adaptive control in this model, with a smaller incremental benefit from forecasting. The system is an educational prototype rather than a validated real-road controller.

## 1. Problem and objectives

Equal green times may waste capacity when traffic demand is uneven. The project aims to build a working simulation, forecast near-term arrivals, implement an adaptive policy, demonstrate image-based counting, compare policies under identical arrivals, and make the process understandable through an interactive interface.

## 2. Architecture

The Python backend trains the model, runs experiments, and produces camera frames and detections. A dependency-free browser interface renders the intersection, queue history, model metrics, and presentation slides.

Two paths are implemented:

- Vision demonstration: generated RGB frame → color mask → connected components → boxes and approach counts.
- Control experiment: generated arrivals → queue state and recent arrival features → forecast → heuristic signal policy → departures and metrics.

The vision module is not connected to the control input. Synthetic scene visibility is capped at nine vehicles per approach. Complete simulation counts are used for control. This explicit separation avoids presenting partial image counts as complete queues.

## 3. Synthetic data and learning

Training generates 300 independent episodes. Each has 36 ten-second arrival-count intervals, with a changing Poisson rate. Sliding windows yield 9,900 training examples. Another 100 independent episodes produce 3,300 held-out test examples. No episode is shared across these sets.

Each feature vector contains arrival counts from the last three completed ten-second intervals in most-recent-first order. The target is arrivals in the next ten seconds. A random forest regressor uses 60 trees, maximum depth 8, minimum leaf size 15, and random state 9. MAE and RMSE measure forecast error; persistence predicts the latest count unchanged.

| Forecast metric | Result |
|---|---:|
| Test MAE | 1.704 vehicles / 10s |
| Test RMSE | 2.203 vehicles / 10s |
| Persistence MAE | 2.061 vehicles / 10s |

These measurements describe synthetic held-out data, not generalization to real roads.

## 4. Computer vision method

Vehicles are rendered as separated blue rectangles on a dark road. The detector selects pixels with high blue and green channels and a lower red channel. A four-neighbor flood fill identifies connected components. Components smaller than 50 pixels are removed. Bounding-box centers assign components to North, East, South, or West image regions.

The method demonstrates image segmentation and counting but assumes controlled color, illumination, separation, and geometry. It has no measured real-video accuracy, occlusion handling, tracking, or learned object classes.

## 5. Control policies and simulation assumptions

The simulator uses one-second time steps, unbounded queues, and one vehicle per second discharge from a single active approach. All arrivals join a queue; a vehicle arriving at an active empty approach can depart in that same second. There is no turning traffic, pedestrian phase, travel time, or intersection geometry model.

The fixed policy rotates N → E → S → W with 25 seconds of green and three seconds with no discharge between phases.

The adaptive policy scores each approach as:

`queue length + 0.7 × predicted arrivals + 0.08 × seconds since green`

Minimum green is 10 seconds and maximum green is 45 seconds. A competing score must exceed the active score by more than two for a normal early switch. Waiting approaches overdue by at least 90 seconds without green receive priority at an eligible decision. Three no-discharge seconds separate phase service. The UI displays these clearance intervals as all-red transitions. The queue-only ablation removes forecast contributions while retaining the other adaptive rules.

These timing and weighting values are design choices, not learned optimal control parameters or certified safety rules.

## 6. Evaluation protocol

Each run lasts 600 seconds. Scenarios are balanced arrivals, North/South rush, and an Eastbound surge in the middle third of the run. Ten seeds (0–9) are evaluated per scenario. The same generated arrival array is replayed for all three policies. This yields 30 paired experiments and 90 policy runs.

Primary delay is queue-seconds divided by all arrivals. Queue-seconds accumulate the queue remaining after discharge each second. The metric includes waiting accumulated by unfinished vehicles, but excludes their waiting after the simulation horizon. Throughput and remaining queues are also reported. Standard deviations are across seeds, not confidence intervals.

| Scenario | Fixed delay mean ± SD | Queue-only delay mean ± SD | ML-assisted delay mean ± SD |
|---|---:|---:|---:|
| Balanced | 38.78 ± 2.23 s | 21.17 ± 1.60 s | 21.11 ± 1.81 s |
| Rush | 99.39 ± 12.69 s | 51.29 ± 10.46 s | 49.10 ± 10.84 s |
| Eastbound surge | 93.34 ± 8.92 s | 33.39 ± 4.51 s | 32.17 ± 3.98 s |

| Scenario | Fixed mean throughput | Queue-only mean throughput | ML-assisted mean throughput |
|---|---:|---:|---:|
| Balanced | 351.7 | 362.0 | 362.7 |
| Rush | 337.0 | 413.8 | 416.2 |
| Eastbound surge | 279.9 | 356.2 | 356.7 |

Adaptation accounts for most of the improvement relative to equal fixed timing. Forecasting contributes a smaller mean improvement, especially under asymmetric demand. The very small balanced-scenario difference should not be interpreted as a robust advantage. No statistical significance or universal superiority is claimed. The fixed baseline is deliberately simple and is not an optimized traffic engineering plan.

## 7. Verification and reproducibility

Eighteen Python tests and seven JavaScript tests verify deterministic arrivals, arrival/departure/remaining conservation, empty-demand behavior, synthetic image counts, no discharge within sampled clearance intervals, and held-out forecasting improvement against persistence. Additional tests verify finite demand-responsive forecasts, past-only model inputs, and changes in actual signal decisions. JavaScript syntax and Python compilation are also checked. `evaluate.py` regenerates all CSV and JSON evidence. Environment and dependencies are described in README.md.

## 8. Limitations and future work

The training distribution and road model are synthetic and simplified. Queue-only adaptation already captures much of the benefit. Controller weights require sensitivity analysis. Real-video counting, detector validation, object tracking, arrival estimation, calibrated traffic flow, turns, pedestrian safety, emergency handling, and failure modes remain future work. More seeds and paired uncertainty analysis are needed before stronger comparative claims.

## 9. Conclusion

FlowState provides a reproducible educational implementation of short-term demand forecasting and adaptive signal decisions, complemented by a transparent computer vision demonstration. It illustrates how to separate prediction quality from control quality and how to evaluate adaptive behavior using common traffic inputs.

### Additional forecast baseline check

The three-window moving-average baseline has held-out MAE 1.733, compared with 1.704 for the random forest. The incremental forecasting benefit over this stronger baseline is modest. A constant training-mean predictor has MAE 2.198. These values are reproducible with `python3 verify_model.py`.

## Interactive prediction update

The Try the Model tab accepts three user-provided recent arrival counts and calls the fitted forest through `/api/predict`. The displayed output includes the expected next count, inputs used, model metadata and a warning for values outside the observed training range. Temporary network failures are retried once; persistent connection errors provide restart guidance.

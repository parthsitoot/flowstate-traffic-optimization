# Understand your project in 10 minutes

## The problem

Traffic lights often use preset timings. Imagine 30 cars on North and only 2 on East. Equal green time wastes capacity on the quiet road while the busy road builds a queue.

## Your goal

Build and evaluate a prototype that changes signal timing according to current queues and predicted near-future arrivals. Compare it fairly with fixed timing. Demonstrate how computer vision can turn an image into a vehicle count.

## The three parts

**Computer vision means extracting information from images.** We draw a synthetic camera frame with blue vehicles. The program identifies blue pixels, groups neighboring pixels into connected components, filters tiny groups, and draws a bounding box around each vehicle. This is actual pixel processing, but it works in a deliberately simple generated scene. It is not YOLO and is not trained for real road videos.

**Machine learning means learning a relationship from examples.** The random forest receives three numbers: vehicles that arrived in the last 10 seconds, the previous 10 seconds, and the 10 seconds before that. It predicts how many will arrive in the next 10 seconds. The examples are generated, not collected from real roads.

**The controller means the decision rules.** It gives each approach a score:

`score = current queue + 0.7 × predicted arrivals + 0.08 × seconds since green`

The largest eligible score generally wins. Green lasts at least 10 seconds and at most 45 seconds. A 3-second all-red interval separates phases. Waiting queues that have not received green for 90 seconds get priority at the next eligible decision. This is starvation mitigation, not a guarantee that every vehicle waits less than 90 seconds.

## Important distinction

The camera panel is a separate demonstration of vehicle counting. The controller currently uses complete internal simulation counts. Camera view holds only 9 vehicles per approach, so it is not a substitute for the full queue. An end-to-end real system would need detection, tracking, arrival estimation, calibration, and safety validation.

## What is a random forest?

A decision tree learns a sequence of questions such as “were recent arrivals above 4?” A forest averages the predictions of many trees. Averaging tends to be more stable than trusting one tree. We use 60 trees. This is supervised regression because the training examples include numeric target counts.

## What are the baselines?

1. Fixed-time: North, East, South, West each get 25 seconds plus a 3-second transition.
2. Queue-only adaptive: adjusts phases using queue and waiting age, with no ML forecast.
3. ML-assisted: same adaptive rules, with an extra forecast contribution.

The first comparison shows the overall value of adaptation. The second tells us whether forecasting adds value beyond observing queues.

## What do the metrics mean?

- MAE: average absolute prediction error. MAE 1.70 means forecasts miss by about 1.7 vehicles per 10-second window, on average.
- RMSE: an error metric that penalizes large misses more strongly.
- Queue-seconds: sum of all waiting vehicles each second. Ten vehicles waiting for five seconds produce 50 queue-seconds.
- Delay per arrival: queue-seconds divided by arriving vehicles during the run. Unfinished vehicles contribute waiting so far, but not future waiting after the run.
- Throughput: vehicles that finished crossing.
- Remaining: vehicles still queued when the experiment ends.

## How to describe the result honestly

“Across ten seeds for the synthetic rush scenario, average measured delay was 99.39 seconds per arrival for fixed timing, 51.29 for queue-only control, and 49.10 for ML-assisted control. Most improvement comes from adaptive control; ML adds a smaller improvement.”

Do not say “AI reduces all real-world traffic by 50%.” We did not test real roads.

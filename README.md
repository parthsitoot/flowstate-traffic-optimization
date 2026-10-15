# FlowState — Smart Traffic Signal Optimization

[![Project checks](https://github.com/parthsitoot/flowstate-traffic-optimization/actions/workflows/checks.yml/badge.svg)](https://github.com/parthsitoot/flowstate-traffic-optimization/actions/workflows/checks.yml)

Repository: https://github.com/parthsitoot/flowstate-traffic-optimization

**Live demo:** https://flowstate-traffic-optimization.vercel.app

A complete ML course prototype: Python traffic simulation, a trained random forest arrival forecaster, classical computer vision on synthetic frames, a polished dashboard, and a nine-slide browser presentation.

## Code, hosting and maintenance

- [Understand the code](docs/CODE_WALKTHROUGH.md): reading order, data flow and where to make changes.
- [Deploy to Vercel](docs/DEPLOYMENT.md): account setup, hosting architecture and verification.
- [Detailed project PDF](output/pdf/FlowState-Detailed-Project-Report.pdf)
- [Short model PDF](output/pdf/FlowState-Model-Summary.pdf)
- GitHub Actions runs the Python tests, model verification and JavaScript syntax check on pushes and pull requests.

## Start here

On this computer, dependencies are already available. From this project folder:

```bash
python3 app.py
```

Open **http://localhost:8000**. Keep the terminal running. If you open `web/index.html` directly from Finder, it redirects to the online app because a local HTML file cannot run the Python model. Internet is not required once dependencies are installed. Click **Presentation mode** for the slides and speaker notes.

For a fresh computer (Python 3.10 or newer):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Windows activation: `.venv\Scripts\activate`. If port 8000 is occupied, close the earlier server using Ctrl+C. The server listens only on your own computer.

## Tomorrow's presentation

1. Read `docs/START_HERE.md` (the plain-language explanation).
2. Read `docs/PRESENTATION_AND_VIVA.md` and rehearse the 5-minute script.
3. Open the live demo or run the app; use Morning rush and run number 42.
4. Read the result card, then show the digital twin, generated camera image, and comparison chart. Point out that this one run is slightly worse than queue-only on waiting per arrival.
5. Open **Try the Model** and submit `[6, 6, 6]` to show a real 5.61-vehicle forecast. Open **Model & methodology**, then **Presentation mode**.
6. Submit the source folder, `docs/REPORT.md`, and `artifacts/` results. The slides are embedded in the app; they are not a PowerPoint file.

## Project structure

- `app.py`: local HTTP server and API.
- `api/`: Vercel Python function entry points.
- `src/service.py`: shared validation, model caching, and request dispatch.
- `src/http_api.py`: serverless HTTP adapter.
- `vercel.json`: static dashboard and Python-function hosting configuration.
- `src/model.py`: synthetic episode generation, random forest training, held-out evaluation.
- `src/simulation.py`: vehicle queues, phase logic, fixed/reactive/ML-assisted comparisons.
- `src/vision.py`: synthetic camera generation, pixel segmentation, connected components, PNG encoding.
- `web/`: offline dashboard and nine-slide presentation.
- `evaluate.py`: 30 experiments, three policies per experiment, CSV and JSON results.
- `tests/test_project.py`: tests for conservation, deterministic arrivals, empty demand, CV counts, transitions, and forecasting.
- `docs/`: report, beginner guide, presentation script, and viva answers.
- `artifacts/`: generated model metrics and experimental evidence.

## Reproduce results

```bash
python3 -m unittest discover -s tests -v
python3 evaluate.py
python3 verify_model.py
```

Training: 300 independent synthetic episodes (9,900 windows). Testing: 100 separate episodes (3,300 windows). Features are the three most recent 10-second arrival counts. Target is next 10-second arrivals. The random forest has 60 trees, max depth 8, minimum leaf size 15. Seeded training runs on the first model request in each server process; no downloaded model weights are required.

## What this project does and does not claim

The ML component predicts arrivals; the controller is a priority heuristic. CV uses genuine image processing on synthetic, known-color vehicles. CV is demonstrated separately: the controller reads the simulation's complete queue and arrival counts rather than camera outputs. There is no trained real-video object detector, live CCTV integration, reinforcement learning, or deployment-ready traffic controller.

All reported improvements are simulation results. The fixed controller is a simple equal-green baseline, not an optimized municipal timing plan. The queue-only comparison isolates the incremental contribution of the forecast. Forecast error improvements alone do not establish control improvements.

## Model verification

`verify_model.py` verifies fitted trees, sensible example predictions, three held-out baselines, and that predictions change actual signal decisions. See `artifacts/model_verification.json`. The forest MAE is 1.704 versus 1.733 for a three-window average; this improvement over a stronger baseline is modest. Forecasts are expected counts and may be fractional. Eighteen Python tests and nine JavaScript tests also check that the simulator passes only past arrival counts to the model.

## Dashboard improvements

The interface uses a compact top navigation, neutral backgrounds, readable system typography, and a single blue accent. Results include a plain-language verdict and explain the comparison methods. The model tab explains decimals, training limits, and test error next to the output. Formulas and deeper assumptions stay in expandable sections.

The comparison chart shows all three policies. Export CSV downloads the selected experiment with its actual run number and all metrics. Camera rendering coalesces slow requests and reuses up to 64 visible queue states. Signal history records the phase active during that second, and peak queues are measured every second.

## Use your own input

Open **Try the Model**, enter the three most recent 10-second arrival counts, and click **Generate prediction**. `[6,6,6]` produces approximately 5.61 expected arrivals. This uses the same trained forest as the simulator. `/api/predict?counts=6,6,6` is available locally and on Vercel. Inputs outside the observed training range are flagged.

If the browser cannot connect, keep `python3 app.py` running and retry. Refresh old tabs after code changes. Another computer or phone needs the deployed URL, not your laptop's localhost URL.

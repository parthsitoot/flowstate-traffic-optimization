# GitHub and Vercel deployment

## Architecture

This repository keeps the same Python ML and simulation implementation for local and hosted use. Vercel serves the static dashboard from `web/`, and routes `/api/model`, `/api/run`, and `/api/vision` to Python functions under `api/`. They all call `src/service.py`.

There are no API keys or environment variables required by the project itself. Hosting requires your GitHub/Vercel account authorization. The app contains synthetic data only and has no user database or sign-in system.

## Import into Vercel

1. Sign in to Vercel and choose **Add New > Project**.
2. Import `parthsitoot/flowstate-traffic-optimization`.
3. Use the repository root. Framework preset: **Other**.
4. `vercel.json` declares `web` as the output directory and the Python functions. No frontend build command is needed.
5. Deploy and wait for a successful build. Check the actual URL Vercel returns.
6. Open `/api/model`: it must return metrics, including 60-tree model behavior through the application. Open the dashboard and run an experiment.

Vercel installs `requirements.txt`. Its current Python runtime supports 3.12; the GitHub workflow checks this version. This project does not require a local port to remain open after deployment.

## Verification checklist

- Home page loads styles and scripts.
- `/api/model` returns JSON containing `mae` and `training_samples`.
- `/api/run?scenario=rush&seed=42` returns 411 ML-assisted served vehicles and delay 54.97 with the recorded dependency environment.
- `/api/vision?q=1,2,3,4` returns counts `[1,2,3,4]` and a PNG.
- Invalid inputs return 400 rather than crashing.
- Browser scenario selection, playback, camera, and presentation work.

Cold starts train a small forest once per process; allow a short initial wait. Separate function processes may each train their own identical model. The website makes no claim of physical real-time control.

## References

- [Vercel Python runtime](https://vercel.com/docs/functions/runtimes/python)
- [Python functions in the api directory](https://vercel.com/docs/functions/runtimes/python/api-directory)
- [Vercel configuration](https://vercel.com/docs/project-configuration/vercel-json)

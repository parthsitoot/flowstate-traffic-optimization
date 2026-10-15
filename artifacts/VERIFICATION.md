# Verification

- Eighteen Python unit tests plus seven JavaScript tests: passed.
- JavaScript syntax check: passed.
- Python source compilation: passed.
- Evaluation: completed 30 seeded experiments / 90 policy runs.
- Browser: dashboard, synthetic CV counts, scenario change, pause, methodology table, and next-slide navigation verified.
- Browser error log: no JavaScript errors during checked interactions.
- Screenshot: dashboard-preview.png.
- Environment versions: environment.json.

The dashboard has been visually inspected at narrow and desktop widths.

- Model-specific verification: passed; fitted forest, reasonable demand response, past-only features, and signal-decision integration. See model_verification.json.

- Local and Vercel HTTP handler smoke tests: HTTP 200; rush seed 42 served 411 vehicles.
- GitHub Actions on Python 3.12: successful initial run 38683431108.
- Vercel hosting is configured but requires account sign-in before deployment can be completed.

- Signal timing regression: exact 3-second no-discharge transitions and 10-45-second adaptive greens verified at every second.
- Peak queue no longer depends on playback sampling.
- Browser: three-policy chart, current queue counts, model baselines, pause and CSV download verified.
- JS regressions: stale fetch/decode results, bounded camera caching, and retry after failure verified.
- Existing mean delay and throughput results remain unchanged after these fixes.

- Try the Model: [6,6,6] -> 5.61, [1,1,1] -> 1.24 verified in browser.
- Experiment rerun successful in the user's refreshed tab; earlier tab retained an old failed-to-fetch message.
- Network retry tested for transient failures and persistent failures; invalid requests are not retried.

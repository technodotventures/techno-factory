# Factory scorecard

> Measurement only — no optimization before 50 runs. Five numbers, one file, trend over runs.

| Run | Date | Task | Cycle time (Discovery→Merge) | Review latency (human-waiting h) | Reverted? | Evidence-pass (1st Test attempt) | Cost |
|---|---|---|---|---|---|---|---|
| 000 | Sep 12→13 2026 | POD-AUDIT-003 — watch actor binding | ~20h wall (~2h worked + overnight wait) | ~18.6h (overnight; offline) | no | ✅ yes (red→green captured) | session-driven; no metered infra. Model spend tracked passively. |

**Notes**
- Run 000 closed Sep 13: merged as [PR #3](https://github.com/technodotventures/pod/pull/3) (`9c24f86`). Metrics are honest wall-clock; review latency for v1 includes an overnight offline period — compare like-for-like on future runs.
- Run 000 was the manual-first smoke: full loop discipline (plan file, red-first test, blind test pass, guard scan, evidence package) executed by the orchestrator; station automation comes next.
- Baseline (pre-fix suite): 285/285 green; fix branch: 287/287 — `runs/run-000/evidence/` holds all outputs.

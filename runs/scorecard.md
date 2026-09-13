# Factory scorecard

> Measurement only — no optimization before 50 runs. Five numbers, one file, trend over runs.

| Run | Date | Task | Cycle time (Discovery→PR) | Review latency (human-waiting h) | Reverted? | Evidence-pass (1st Test attempt) | Cost |
|---|---|---|---|---|---|---|---|
| 000 | Sep 12 2026 | POD-AUDIT-003 — watch actor binding | ~2h (first run; includes harness setup) | pending | — | ✅ yes (red→green captured) | session-driven; no metered infra. Model spend tracked passively. |

**Notes**
- Run 000 is the manual-first smoke: full loop discipline (plan file, red-first test, blind test pass, guard scan, evidence package) executed by the orchestrator; station automation comes next.
- Baseline (pre-fix suite): 285/285 green — `runs/run-000/evidence/` holds the runs.

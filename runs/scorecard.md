# Factory scorecard

> Measurement only — no optimization before 50 runs. Five numbers, one file, trend over runs.

| Run | Date | Task | Cycle time (Discovery→Merge) | Review latency (human-waiting h) | Reverted? | Evidence-pass (1st Test attempt) | Cost |
|---|---|---|---|---|---|---|---|
| 000 | Sep 12→13 2026 | POD-AUDIT-003 — watch actor binding | ~20h wall (~2h worked + overnight wait) | ~18.6h (overnight; offline) | no | ✅ yes (red→green captured) | session-driven; no metered infra. Model spend tracked passively. |
| 001 | Sep 13 2026 | Coffee MCP token helper — card `M1s37…` | ~25 min wall | 21s (PR open→merge) | no | ✅ yes (red→green 9/9) | session-driven; no metered infra |
| 002 | Sep 13 2026 | Pod audit 002 — hash agent bearer tokens — [pod#4](https://github.com/technodotventures/pod/pull/4) | ~33 min wall (card 14:22Z → PR 14:55Z) | ~22h (PR 14:55Z → merged Sep 14 13:18Z; overnight) | no | ✅ yes (red→green first pass; 290/290) | session-driven; native Planner run $0 |
| 004 | Sep 14 2026 | Pod E2E test kit — Playwright + a11y + visual + CI — [pod#5](https://github.com/technodotventures/pod/pull/5) | ~48 min wall (card 10:00Z → CI green 10:48Z) | ~1h45m (IN REVIEW 10:36Z → merged 12:22Z) | no | ✅ yes (first run red incl. 18 real a11y findings; mutation-red captured; 17/17 local + CI green) | session-driven; $0 tooling; CI minutes within free tier |
| 005 | Sep 14 2026 | Pod deps 005 — clear the beta-gate — [pod#6](https://github.com/technodotventures/pod/pull/6) | ~23 min (card 13:23Z → merged 13:45Z) | ~4 min (IN REVIEW 13:42Z → merged 13:45:45Z) | no | ✅ yes (audit 5→0 red→green; beta-gate green on main first time since Sep 8; 290/290 + 17/17; CI both green) | $0; deps-only |
| 006 | Sep 14 2026 | CI self-heal pilot — detect → brief → fix (factory capability) | ~40 min build+demo (14:42Z → 15:22Z) | n/a (internal capability; no human PR) | no | ✅ yes (live red→brief→fix→green on a throwaway branch; guards verified: superseded / merged-branch / closed-PR) | $0 (script + cron; gh API free) |

**Notes**
- Run 000 closed Sep 13: merged as [PR #3](https://github.com/technodotventures/pod/pull/3) (`9c24f86`). Metrics are honest wall-clock; review latency for v1 includes an overnight offline period — compare like-for-like on future runs.
- Run 002 closed Sep 14: merged as [PR #4](https://github.com/technodotventures/pod/pull/4) (`48f5adf`, 13:18Z).
- Run 004 closed Sep 14: merged as [PR #5](https://github.com/technodotventures/pod/pull/5) (`daf7219`, 12:22Z); post-merge E2E green on main.
- Run 005 closed Sep 14: merged as [PR #6](https://github.com/technodotventures/pod/pull/6) (`c9889ae`, 13:45Z). **Repo green everywhere** — beta gate green on `main` for the first time since Sep 8.
- Run 006: CI self-heal live — `ci-heal` watchdog (hermes cron, every 30m) briefs red CI on factory branches + `main` to `runs/ci-heal/` and the factory channel; fix lane agent-operated. Demo + honest notes: `runs/run-006/`.
- Run 000 was the manual-first smoke: full loop discipline (plan file, red-first test, blind test pass, guard scan, evidence package) executed by the orchestrator; station automation comes next.
- Baseline (pre-fix suite): 285/285 green; fix branch: 287/287 — `runs/run-000/evidence/` holds all outputs.

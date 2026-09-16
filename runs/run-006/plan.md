# Run 006 — plan (CI self-heal loop: detect → brief → fix)

- **What:** the factory's first self-heal capability. When CI goes red on a factory branch (or `main`), the factory should detect it *without anyone watching*, produce a diagnosis brief, and route it to a worker who fixes and re-verifies.
- **Scope (pilot):**
  - `scripts/ci-heal.py` — scans recent failed runs (`factory/*` + `main`) across the factory repos via `gh`; skips superseded failures (a newer green run) and in-flight re-runs; extracts the failed step + error excerpt; classifies (deps/runtime/typecheck/unit/e2e/install); writes a brief to `runs/ci-heal/`; posts one notification to the Coffee channel. State file prevents duplicates.
  - Always-on cadence: a scheduled job runs the scan every 30 minutes.
  - **Fix lane stays agent-operated** (by design): a worker (human or agent) picks up the brief and runs the repo's red→green loop. Full auto-fix becomes a later increment once briefs prove reliable.
- **Demo (this run's evidence):** a throwaway branch (`factory/ci-heal-demo` on pod) with one deliberately failing test → CI goes red → the detector catches it live, briefs it, notifies the channel → the failure is removed → CI goes green → detection state shows superseded-skip.
- **Why now:** we've had two red-CI incidents this week that needed a human to notice + diagnose (watch-auth/Node 22 class, audit). The trigger material exists; this closes the "nobody was watching" gap.

## Evidence plan

demo branch push → red runs → `ci-heal` scan output + brief file + Coffee message → fix commit → green runs → second scan shows `superseded-skip`. Records in `runs/ci-heal/` + `runs/run-006/`.

## Out of scope

Auto-fix without a worker; cross-repo alerting beyond the two factory repos; GitHub-side workflow changes.

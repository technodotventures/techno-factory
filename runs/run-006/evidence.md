# Run 006 — evidence (CI self-heal loop: detect → brief → fix)

> Mission check: *did this actually happen?* Every claim maps to a live GitHub run, a file in this repo, or a Coffee message.

- **Capability:** `scripts/ci-heal.py` — scans failed workflow runs (`factory/*` branches + `main`) across the factory repos; skips superseded failures (newer green), merged/closed-PR branches, and in-flight re-runs; extracts the failed step + error excerpt; classifies (deps/runtime/unit/e2e/typecheck/install); writes a brief to `runs/ci-heal/<run-id>.md`; posts ONE Coffee notification per new failure. State file (`runs/ci-heal/state.json`) dedupes.
- **Schedule:** hermes cron `redacted-id-35` — `ci-heal-job.sh`, every 30m, no_agent mode. Launcher lives in the profile's hermes scripts dir and execs `techno-factory/scripts/ci-heal.py`. Gateway started manually (`hermes gateway run`, PID 708063 at setup — container runtime; durable restart policy is not settable from inside the container).
- **Fix lane stays agent-operated** (pilot scope): a worker picks up the brief and runs the repo's red→green loop.

## Live demo — throwaway branch `factory/ci-heal-demo`, draft PR #7

| step | evidence |
|---|---|
| deliberate failure pushed | `83c8a6a`; PR #7 (draft, "do not merge") |
| **red** | E2E fail 3m30s (run 34858434761) · Beta gate fail 4m13s (run 34858434675) |
| **detect + brief + notify** | scan output below; briefs `runs/ci-heal/34858434761-e2e.md`, `runs/ci-heal/34858434675-beta-gate.md`; one Coffee message posted to the factory channel |
| **fix pushed** | `dbc8baf` (removes the failing test) |
| **green** | E2E pass 5m8s (run 34858957835) · Beta gate pass 5m4s (run 34858957837) |
| cleanup | PR #7 closed with the full story; remote + local branch deleted; worktree removed |

## Scan outputs (verbatim)

Red-state scan:

```text
briefed technodotventures/pod 34858434761 E2E on factory/ci-heal-demo [TYPECHECK] -> 34858434761-e2e.md
briefed technodotventures/pod 34858434675 Beta gate on factory/ci-heal-demo [TYPECHECK] -> 34858434675-beta-gate.md
skip (branch PR merged) technodotventures/pod 34849720088 Beta gate factory/fix-deps-audit
skip (superseded) technodotventures/pod 34848484024 Beta gate main
skip (superseded) technodotventures/pod 34843032300 Beta gate main
skip (branch PR merged) technodotventures/pod 34833462743 Beta gate factory/feat-e2e-kit

briefed: 2 · tracked total: 6
```

Post-close re-scan (guards hold; no re-notification):

```text
skip (branch PR closed) technodotventures/pod 34858434761 E2E factory/ci-heal-demo
skip (branch PR closed) technodotventures/pod 34858434675 Beta gate factory/ci-heal-demo

briefed: 0 · tracked total: 6
```

## Honest notes

- **Classifier v1 mislabeled the demo failure** `TYPECHECK` (it read the log head, which contains the step's `typecheck` echo). Fixed to step-name bias + failure-excerpt-first; the two briefs were regenerated to `UNIT-TEST` (the Coffee message from the first pass still says TYPECHECK — the brief files are corrected).
- The first dry-run scan surfaced a pre-guard false positive (a merged branch's old failure) → added the merged/closed-PR guard; re-verified via the stale skips above.
- `--dry-run` now writes no files and no state.
- The demo branch's red runs remain visible in GitHub history (run IDs above) — the record survives the branch deletion.

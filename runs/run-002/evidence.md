# Run 002 — evidence (Pod audit 002: hash agent bearer tokens)

- **Status:** ✅ **PR #4 open for review** — [technodotventures/pod#4](https://github.com/technodotventures/pod/pull/4) (shortlink: `tinyurl.com/23tk5zma`), created 14:55:33Z. Card `redacted-id-28` → **IN REVIEW** (status event logged, 14:56Z).
- **Cycle:** 14:22:50Z card → 14:55:33Z PR ≈ **33 min wall**. Review latency: pending founder review.
- **Evidence artifacts:** on the card (grouped under "Made by Factory Planner"): red, green, full suite, guard scan.

## RED → GREEN

- **RED** (`evidence/red-agent-token-hash.txt`): 3 failures pre-fix — `raw bearer must not be stored` (actual = the raw `cpod_agent_…`), `stored bearer is never re-readable` (connection returned raw), `legacy plaintext is replaced by its hash`.
- **GREEN** (`evidence/green-agent-token-hash.txt`): 3/3 pass — storage-is-hash, auth-by-hash + rotation over HTTP, connection reveal rotates, legacy migration incl. idempotency across re-opens.
- **Full suite** (`evidence/full-suite.txt`): **290/290** (baseline 287 + 3 new).
- **Guard scan** (`evidence/guard-scan.txt`): clean — 4 files, no blocked paths, no lockfile churn.

## Criteria coverage (Planner criteria → proof)

| # | Criterion | Proof |
|---|---|---|
| 1 | First proof step red-first | RED run, test 1 first assertion |
| 2 | Returned once, hash stored | test 1 (stored == sha256(token); raw unreadable; reads null) |
| 3 | Auth by hash | test 1 (`getAgentByToken` + watch upgrade 101) |
| 4 | Rejection parity | test 1 (unknown bearer null; rotated-out bearer 401 over HTTP) |
| 5 | Migration + token keeps working | test 3 |
| 6 | Zero `cpod_agent_` rows after | test 3 (equality with sha256) |
| 7 | Idempotent re-run | test 3 (second open, no error) |
| 8 | Same scheme as client tokens | both `sha256` hex; note: separate modules, scheme-identical (no salt/pepper anywhere) |
| 9 | Tests pass, output attached | suite 290/290 + 4 artifacts on card. No CI pipeline in repo — local run output attached; CI link not available. |
| 10 | Client-token behavior unchanged | full suite incl. client-token tests green |

## Behavior changes (documented in the PR)

1. Agent update responses no longer return the token (`null`) — unrecoverable by design.
2. `GET …/connection?reveal=1` rotates instead of unmasking; without reveal: `token: null` + `has_token`.
3. Re-spawn of an existing child rotates its bearer.

## Dogfood findings (native-first loop)

- **#3 — Planner has no repo access:** its "surfaces likely touched" names file *roles*, not paths (agent said so on the card). Criteria stayed behavioral-strong; the Spec↔repo bridge (worker context, or a codebase graph per the Graphify pilot) is the missing link for path-level planning.
- **#4 — no checklist-read tool exposed:** items can only be read from activity events; verdict-marking per item is limited. Ask: `GetTaskChecklist`.

## Run log

14:22:50 card created → 14:22:50 Planner assigned (API, `PostAiAgentsAssignTask`, enqueued) → 14:23:29 plan comment + 10 criteria posted natively (1 turn, $0) → 14:30–14:50 build (RED captured, fix, GREEN, suite) → 14:55:33 PR #4 (via `gh`, from this environment) → 14:56 card IN REVIEW → 14:58 audit doc row marked fixed within the PR.

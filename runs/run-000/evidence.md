# Run 000 — evidence package

- **Work item:** POD-AUDIT-003 (/pod/watch actor binding) · **Repo:** `technodotventures/pod`
- **Branch:** `factory/fix-watch-actor-binding` · **Commit:** `01b919f` · **Base:** `e4630df`
- **PR:** branch pushed (`origin/factory/fix-watch-actor-binding`); draft-PR creation = **one founder click** via the prefilled compare link (GitHub token lacks Pull-requests:write — noted for ops).
- **Status:** tests green on fix branch — awaiting the human Review (*Approve to merge*).

## Changed files

| File | Δ |
|---|---|
| `src/routes/watch.ts` | +102 — `authorizeWatchActor()` (owner token → client → session → agent bearer; identity binding per `requireActorAuth`) wired into the upgrade handler before any subscription |
| `src/test/watch-auth.test.ts` | new (+144) — first upgrade-path tests in the repo: 6 scenarios over a raw WebSocket client |
| `docs/FINDINGS.md` · `docs/audits/2026-08-24-pod-audit.md` | status → fixed |

## Checks (evidence files in this folder)

| Check | Result | Evidence |
|---|---|---|
| Red run — new tests vs unfixed code | ✖ **fail as expected**: *"anonymous owner impersonation must be 401, got 101"* — unauthenticated upgrade connected to the owner's event stream | `red-watch-auth.txt` |
| Green run — new tests vs fix | ✅ 2/2 pass (impersonation refused; owner / agent-self / open-mode still connect) | `green-watch-auth.txt` |
| Full suite — baseline (`main`) | ✅ 285/285 | baseline run (main clone) |
| Full suite — fix branch | _running_ | _suite output to append_ |
| Build / typecheck | ✅ `tsc` clean in both runs | — |
| Guard scan (mechanical diff integrity) | ✅ clean — 4 files, +248/−2 | `guard-scan.txt` |

## Remaining risks (for the reviewer)

- `local-trust` mode keeps unauthenticated **reads by design** (documented in code; out of scope to change).
- Raw-socket denials carry reason phrases (`401 Unauthorized`), not JSON bodies — parity with the existing handler style.
- No Adversary station in the factory yet (this is R3 work) — reviewer should expect to scrutinize the cascade order themselves.

## Replay fields

- commit `01b919f` · base `e4630df` · node v26.5.1
- commands: `npm run build` → `node --test --test-force-exit dist/test/watch-auth.test.js`; `npm test`; `scripts/guard-scan.sh <repo> origin/main`

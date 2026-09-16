# run-009 evidence — Telemetry: per-source observation stats readable by agent tokens

- Worktree: `/opt/data/dev-workspaces/worktrees/pod-run007` · Branch: `factory/feat-telemetry-stats` (base `main` @ `0e592fe`) · Commit: single commit on this branch (see `git log -1`).
- Deliverable: new read-only `GET /pod/telemetry/sources` so silent memory loss (captures that never reach REFLECT) is observable from inside the product. Owner-only `GET /pod/telemetry` is unchanged.

## Scope

Per-`source_id` stats: `active_count`, `retired_count`, `total_count`, `last_capture_at` (MAX `created_at`), `object_count` (distinct objects), `claims_created` (SUM `objects.reflection_claim_count` over distinct objects). Aggregatable by prefix (`?prefix=hermes-bookmarks:` → matched sources plus an `aggregate` block). `?source_id=` exact lookup echoes the requested id with zero counts when unknown/invisible (never an error). `?since=` filters `created_at`. Global `reflect` block: `last_reflected_at`/`cadence_mode`/`next_reflect_after` (from `pod.reflect_cadence` settings) and `last_event_at`/`last_event_type` (latest `events` row with `process='reflect'`). Out of scope and untouched: no UI, no alerting, no mutation path, no new agent permission beyond reading these stats.

Auth: new `requireStatsReadAuth` (src/security/auth.ts) accepts owner/session/client/agent for reads only — existing `requireOwnerAuth`/`requireActorAuth` untouched. Agent-kind callers are intersected with their active `agent_collection_grants` (revoked grants excluded): only observations of objects in granted collections are counted; an agent with no grants sees zero sources. Owner/session/client are unfiltered.

## Approach / files changed (`git diff --stat`)

| File | Change |
|---|---|
| `src/pod/db.ts` | +106: `PodSourceObservationStats` + `aggregateObservationStatsBySource(db, {sourceId, prefix, since, collectionIds})` — two-level SQL (status counts + distinct-object lineage/claims), LIKE-escaped prefixes, empty `collectionIds` ⇒ no rows. `claims_created` approximation documented in-code (object-level claim count attributed to each observing source; Pod records no per-source claim provenance). |
| `src/security/auth.ts` | +28: `requireStatsReadAuth` (owner/session/client/agent; read-only). |
| `src/routes/telemetry.ts` | +127/-2: `GET /pod/telemetry/sources`; grant intersection; zero-fill for exact unknown ids; `aggregate` block when `prefix` present; `reflect` block with `per_source: 'not_tracked'` + note (per-source reflect status does not exist — not invented). `source_id` takes precedence over `prefix`; invalid `since` ⇒ 400 `invalid_since`. |
| `src/test/telemetry-sources.test.ts` | new: node:test, 2 tests / 10 scenarios (counts, prefix+aggregate, literal LIKE escaping, unknown→zeros, `since`, reflect block, idempotent re-record, no mutation methods, agent read, grant intersection, revoke, owner-only surface unchanged). |

User-facing shape captured from a real run: `api-sample.txt`.

## Commands run (all from the worktree; full raw output in this directory)

```
npm run build
node --test --test-force-exit dist/test/telemetry-sources.test.js        # RED  -> red-first.txt (exit 1)
# ... implementation ...
npm run build
node --test --test-force-exit dist/test/telemetry-sources.test.js        # GREEN -> included in test-final.txt:290-291
npm run typecheck                                                        # exit 0 -> typecheck.txt (12 lines, no diagnostics)
npm run lint                                                             # exit 0 -> lint.txt (design-lint warnings only, all pre-existing ui/src/main.tsx)
npm test                                                                 # run 1 -> test-final-run1-flake.txt (291/292, flake below)
npm test                                                                 # rerun -> test-final.txt (292/292 green)
git stash push -u -m run-009-baseline-check && npm run build \
  && node --test --test-force-exit --test-name-pattern="Connected OpenAI keys power" dist/test/pod-flow.test.js   # base: 1/1 pass; then git stash pop
node --test --test-force-exit --test-name-pattern="Connected OpenAI keys power" dist/test/pod-flow.test.js        # branch: 1/1 pass
node .run009-sample.tmp.mjs                                              # -> api-sample.txt
```

## Test counts

- RED (pre-implementation): `tests 2, pass 0, fail 2` — both `Route GET:/pod/telemetry/sources not found` 404 (`red-first.txt`).
- Targeted GREEN: 2/2 pass (`test-final.txt` lines 290–291).
- Full `npm test` run 1: `tests 292, pass 291, fail 1` (`test-final-run1-flake.txt`).
- Full `npm test` rerun: `tests 292, pass 292, fail 0` (`test-final.txt`, 384.9 s).

## Flake triage — "Connected OpenAI keys power Ask Pod answers and reflection compile" (`pod-flow.test.js`)

Run 1 failed `assert.ok(compile.json().pages_compiled >= 1)` at 363 ms. Not reproducible: the identical full suite on this branch passed it (684 ms, 292/292) and the operator's full-suite run on clean `main` (`/opt/data/workspaces/uploads/main-suite-run1.log`) passed it too (626 ms; main suite 290/290 — 2 fewer tests because the new test file is branch-only). Isolated `--test-name-pattern` runs pass on both the stashed base state and the branch code. run-009 touches nothing on that path (new read-only stats route; additive db/auth helpers; no changes to compile/OpenAI/provider code, and `pod-flow.test.js` was not modified). Labelled **flake-suspect**, suite-order/load dependent, not attributable to run-009.

## Deviations / leftovers (honest list)

- Per-source "last synthesis timestamp" does not exist in the data model; the response states `reflect.per_source: 'not_tracked'` and carries the global reflect block instead. Silent-loss signal documented in the response note: compare a source's `total_count`/`claims_created` growth against `reflect.last_reflected_at`.
- `claims_created` is an approximation (see db.ts comment): object-level claim counts are attributed to every source that observed the object.
- Agent kind with `access_mode: 'all'` but no collection grants sees zero sources (strict grant intersection, deliberately conservative). Client-kind tokens are treated like owner/session for this read surface (brief filters only `agent`).
- `since` with an unparseable value returns 400 `invalid_since`; `aggregate` is returned only when `prefix` is given; exact `source_id` wins over `prefix` when both are present.
- Smartware authority gate: classified as **Pod product behavior** (read-only observability over Pod's own SQLite tables; no wire/storage/canonical-shape change, no new Smartware grant, Smartware package untouched).

## Merge receipt

- **Merged:** PR #11 squash-merged to `main` @ `48223f0f956434860a454802ae6e888c6298b162` (2026-09-16 23:52:22Z).
- **Approval:** founder **one-off** (explicit, in-session); checks hand-verified via the Actions API on the frozen head `9b4ddfe` (E2E ✅ · Beta gate ✅). Native decision `td_5e01011e-8832-4b2c-a13a-a5299e72d9ba` superseded by the one-off.
- **Review:** 4 evidence cycles (3× NOT VERIFIABLE → evidence-delivery fix → 2 MET · 1 partial); criterion-1 rescope accepted with the merge. Mechanism documented: `docs/coffee-integration.md` §6j.
- **Card:** [Pod] Telemetry `eEKUAAzijladyNdo8e7HLq2q` → **COMPLETE** (10/10 ticked), receipt posted, channel notified.

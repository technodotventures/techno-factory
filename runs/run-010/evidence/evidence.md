# run-010 — batched OBSERVE ingress (Pod)

**Card:** t5YRLmBWVhg2bCump7xep3R6 · **Branch:** `factory/feat-observe-batch` (off `main` @ `48223f0`) · no push, no PR.
**Brief:** `POST /pod/observe` accepts a bounded array of operations (≤ 100 per request); each item
carries its own `operation_id` with per-item idempotency; the response reports per-item outcomes
(accepted · duplicate · rejected-with-envelope) so partial success is representable; the existing
single-operation shape keeps working unchanged.

## Scope / approach

- Route grounded in the actual code: the harness-facing ingress is **`POST /pod/observe`**
  (`src/routes/pod.ts` line ~1679); `/pod/reflect` from the plan draft is a different verb and was
  not touched.
- Batch is selected by the presence of an `items` field on the same route — no new route, no change
  to the single-operation branch. The route body schema now uses `anyOf`: branch 1 is the *verbatim*
  single-operation schema (`required: ['content','operation_id']`), branch 2 adds `items`
  (`required: ['items']`). Single-operation validation behavior is therefore byte-identical.
- Each item runs through the **existing single-operation path**: same experience-event validation,
  same actor auth (`requireActorAuth`), same scope resolution + `requireAgentScope`, same
  `wrapMutation` / `operations_seen` per-`operation_id` idempotency, same substrate
  (`core.observe`), same best-effort activity event. Nothing about storage, memory semantics or the
  Smartware contract changed.
- Per-item failures never abort siblings: shared helpers that answer by writing to the Fastify reply
  (`requireActorAuth`, `requireAgentScope`, `handleOperationError`/`specError`) are invoked against a
  small capturing reply, and whatever they wrote becomes that item's result. Results are collected
  in request order, so a batch is processed **sequentially on purpose** — intra-batch duplicate
  detection (item 2 duplicating item 1) depends on item 1 having committed first.

### Wire contract (batch)

Request (additive to the existing shape):

```json
{ "actor_id": "hermes", "items": [ { "operation_id": "op_…", "content": "…", "scope_alias": "…", "source_id": "…" } ] }
```

Each item may also carry `actor`/`actor_id` (defaults to the batch-level actor), `type`, `scope`,
`content_format`, `visibility`, `sensitive`, `informed_by`, `source_id`. `items` must be an array of
1–100 entries; max batch size is `OBSERVE_BATCH_MAX_ITEMS = 100`.

Response:

```json
{
  "ok": false,
  "batch": { "received": 3, "accepted": 1, "duplicate": 1, "rejected": 1, "max_items": 100, "status": "partial" },
  "results": [
    { "index": 0, "operation_id": "op_…", "status": 201, "outcome": "accepted",  "result": { "id": "obs_…", "status": "accepted", "sequence": 1 } },
    { "index": 1, "operation_id": "op_…", "status": 200, "outcome": "duplicate", "result": { "id": "obs_…", "status": "accepted", "sequence": 1 } },
    { "index": 2, "operation_id": "NOT-A-OPERATION-ID", "status": 400, "outcome": "rejected",
      "error": { "code": "invalid_payload", "message": "operation_id 'NOT-A-OPERATION-ID' does not match ^op_[0-9A-HJKMNP-TV-Z]{26}$", "details": { "received": "NOT-A-OPERATION-ID" } } }
  ]
}
```

- `results` is positional (`index`), one entry per submitted item — repeated `operation_id`s each get
  their own entry (no collision, no overwrite).
- Per-item `status`: `201` accepted · `200` duplicate · `400`/`409`/`403`/`422` rejected.
  `error` is the standard Protocol Contract v0.4.1 envelope body `{ code, message, details? }`.
- Overall HTTP status: `200` all items succeeded · `207` partial success · `400` nothing in the batch
  succeeded. Empty / non-array / missing `items` and > 100 items are whole-request `400`s
  (`{ error: { code: 'invalid_payload', … } }`) — no per-item results exist for those.
- Per-item idempotency is unchanged: same `operation_id` + same payload ⇒ `duplicate` (cached result,
  no new write); same id + different payload ⇒ `409 conflict`; malformed id ⇒ `400 invalid_payload`
  (never a `500`). A fresh `operation_id` whose `source_id` already identifies an observation is
  reported `duplicate` (substrate-level dedupe) rather than claiming a new artifact.

### Smartware authority gate (AGENTS.md)

Classified as **Pod product behavior / harness-facing ingress**: a Pod-side batch adapter over the
existing per-operation materialization path. No canonical wire/storage behavior, memory semantics or
authorization change, no new Smartware release consumed, so no Smartware-first work and no vendor
lockfile update. `wrapMutation` + `operations_seen` semantics and the substrate call are reused
verbatim.

## Files

| File | Change |
| --- | --- |
| `src/routes/pod.ts` | `anyOf` body schema (single-op branch unchanged); batch dispatch; `captureReply`, `runObserveBatchItem`, `runObserveBatch`, `recordObserveBatchActivity` helpers; `isRecord`, `OBSERVE_BATCH_MAX_ITEMS`, `ObserveBatchItemResult` |
| `src/test/observe-batch.test.ts` | new — 9 node:test cases (red-first) |
| `README.md` | route list notes the bounded batch form |
| `docs/install.md` | bulk-import curl example + per-item outcome/status rules |

## Criteria → evidence mapping

| # | Criterion | Test (all in `src/test/observe-batch.test.ts`) |
| --- | --- | --- |
| 1 | RED-GREEN: malformed `operation_id` in a batch → per-item error, standard envelope | `batch: malformed operation_id yields a per-item error envelope while siblings succeed` — RED before (`red-first.txt`), GREEN after |
| 2 | N valid ops → N per-item results tagged with the caller's exact `operation_id` | `batch: N valid operations return N results tagged with the caller operation_ids` |
| 3 | One failed item does not prevent siblings succeeding (independently reported) | `batch: a rejected item does not abort its siblings` (survivors replay as `duplicate` ⇒ they really committed) |
| 4 | Malformed `operation_id` item → 400 standard envelope, not 500 | `batch: malformed operation_id items return 400 envelopes, never a 500` (all-malformed batch ⇒ HTTP 400; single-op malformed ⇒ 400 invalid_payload) |
| 5 | Existing single-operation shape unchanged | `batch: the existing single-operation request shape is unchanged` (also passes on pre-change code — regression guard) |
| 6 | Empty batch / missing `items` → whole-request validation error | `batch: empty, missing, and oversized batches are rejected at the request level` (also 101 items ⇒ 400) |
| 7 | Duplicate `operation_id`s in one batch each distinguishable | `batch: repeated operation_ids in one batch stay distinguishable` (accepted + duplicate + conflict, all echoing the same id) |
| 8 | typecheck + unit + lint/design-lint pass | `typecheck.txt`, `test-final.txt`, `lint.txt` |
| — | Brief: 100 items in one request; real request/response sample; substrate dedupe honesty | `batch: a 100-item request is accepted in one call with 100 outcomes`, `batch: substrate-level source_id dedupe is reported per item`, `api-sample.txt` |

## Commands and results (raw output in this directory)

```
npm run build                       # tsc, clean (used for the targeted red/green loop)
node --test --test-force-exit dist/test/observe-batch.test.js   # RED  → 1 pass / 7 fail   (red-first.txt)
                                                                # GREEN → 9 pass / 0 fail   (targeted-test.txt)
npm run typecheck                   # tsc --noEmit (server + ui) → exit 0                  (typecheck.txt)
npm test                            # clean + build + full node:test suite
                                    #   tests 301 · pass 301 · fail 0 · 351.6s · exit 0    (test-final.txt)
npm run lint                        # typecheck + oxlint/@shadcn design lint → exit 0
                                    #   0 errors, 262 pre-existing warnings (all ui/src/main.tsx,
                                    #   untouched by this change)                             (lint.txt)
node evidence/observe-batch-sample.mjs   # real request/response + timing                  (api-sample.txt)
node evidence/openapi-check.mjs          # /docs/json still generates: 171 paths, observe body anyOf ✓ (openapi-check.txt)
```

Full suite: **301/301 pass, 0 fail** (includes the 9 new tests). Nothing failed, so no
retry/baseline (`git stash`) pass was needed; unrelated tests were not modified.

## Deviations / notes

1. **Route:** implemented on `/pod/observe` (per the brief and the existing harness/test call sites,
   `src/test/*` all post there). `/pod/reflect` was left alone.
2. **Field name:** `items` (the criterion text names an "items field"). A bare JSON array body or an
   `operations` alias was **not** added, to keep one documented contract; both were considered.
3. **Perf:** the per-item substrate work is intentionally identical to a single call, so the win is
   per-request overhead: loopback HTTP 100 items = **929 ms batched vs 1747 ms sequential (1.88×)**;
   in-process `inject` = ~equal (1.00–1.6× across runs — inject overhead is ~1 ms/request, substrate
   work dominates). Structurally the backfill drops from 270 round trips (and 270 client-side ULID
   generations/timeouts) to 3 requests of ≤100 items; over a real network the per-round-trip cost is
   much larger than on loopback. Reported as measured, not asserted.
4. **Substrate dedupe discovery:** while testing, `core.observe` reported `status: "duplicate"` for a
   second item sharing a `source_id` — i.e. observations are deduped by `source_id` at the substrate
   level. The batch reports that honestly as `outcome: "duplicate"` (status 200) and the test suite
   pins the behavior; the 100-item test therefore uses distinct per-item `source_id`s.
5. Design lint covers `ui/src` only; this change is server-side, so no design-rule surface changed.
6. Not done (out of scope): `/pod/reflect` batching from the same plan document — that is the sibling
   card ("this pairs with the reflect batching issue").

## Merge receipt

- **Merged:** PR #12 squash-merged to `main` @ `dd91bef15e84a621c5372e27e448af2dd1f764b7` (2026-09-17 02:36:14Z).
- **Approval:** founder in-session ("approve"); merge rail dry-run for the record = R1/R2/R3/R5 PASS (R4 by founder instruction, chain recorded); native decision `td_3a04588a-a87d-4275-9426-bbd339f498a4` superseded.
- **Review:** 4 cycles — final position 3 MET + criterion-4 rescope accepted; C3 = transient reviewer-context anomaly (documented, superseded by C4).
- **Card:** [Pod] observe `t5YRLmBWVhg2bCump7xep3R6` → **COMPLETE** (8/8 ticked), receipt posted, channel notified.

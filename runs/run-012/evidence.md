# Run-012 — evidence

- **Card**: `N9zHVtucPsjsx9RthfOkIyDT` (Pod Factory) — **COMPLETE** (7/7 criteria ticked)
- **Branch / head**: `factory/fix-smartware-deepseek-fallback` @ `87bce41`
- **Base**: `origin/main` `ccba1fb`
- **PR**: [pod#14](https://github.com/technodotventures/pod/pull/14) — squash-merged as **`e0ace62`** at **2026-09-18T03:49:27Z**
- **Gate**: all five merge rails PASS; approval = the founder's human-posted card comment (03:48:40Z) — **47 s from approval to merge**
- **Review**: cycle 1 = 6 MET + 1 PARTIAL (evidence gap, not product) → receipts attached → re-roll = **7/7 MET, gaps: none**
- **Worktree**: `/opt/data/dev-workspaces/worktrees/pod-run012`
- **Outcome**: shipped to `main`; the founders' box moved to clean `main` and verified live

## Checks

| Check | Command | Result |
| --- | --- | --- |
| RED first (pre-fix) | `node --test dist/test/smartware-llm-config.test.js` on `ccba1fb` | **2 fail / 4 pass** — `provider: 'none'` vs expected `'deepseek'` (`red-first.txt`) |
| Targeted GREEN (post-fix) | same file, `87bce41` | **6/6 pass** (`green-targeted.txt`) |
| Typecheck | `npm run typecheck` | rc=0 |
| Design lint | `npm run lint:design` | rc=0 (toolchain lent from the run-007 worktree — the linked `node_modules` lacks `oxlint`/`@shadcn/lint`; `ui/src` untouched; warnings only) |
| UI unit tests | `npm run test:ui` | rc=0 |
| Build | `npm run build` | rc=0 |
| Backend suite | `node --test dist/test/**/*.test.js` | 307 tests · 306 pass · 1 fail (labeled flake, below) |
| Guard scan | `bash scripts/guard-scan.sh <worktree> origin/main` | **clean, 2 changed files, no findings** |
| CI (PR) | Beta gate + E2E on head `87bce41` | **both success** (Beta gate 3m42s; E2E 6m46s incl. unit+integration, Playwright journeys/a11y/visual) — `ci-receipts.txt` |

## Changed files

- `src/services/ai-provider.ts` (+12 / −2) — DeepSeek fallback in `syncSmartwareLLMConfig`.
- `src/test/smartware-llm-config.test.ts` (+128) — 6 cases: fallback default model · `DEEPSEEK_MODEL` honoured · no key stays `none` · codex never replaced · active provider wins · idempotent re-run.

## Flake receipts (ours-vs-pre-existing split)

Full suite on the branch: **1 failure, not ours** — `dist/test/pod-flow.test.js` → `/pod/query returns the matching claim instead of an unrelated high-confidence sibling` (`assert.ok(deadlineVersion)` undefined). The diff touches neither retrieval nor pod-flow.

| Run | Result | Log |
| --- | --- | --- |
| Full suite, branch `87bce41` | 1 fail (the pod-flow claim test) | `test-full.txt` |
| Standalone on the branch, run 1 | **11 pass / 0 fail** | `flake-branch-run1.txt` |
| Standalone on the branch, run 2 | **11 pass / 0 fail** | `flake-branch-run2.txt` |
| Standalone on clean `main` (`ccba1fb`) | **11 pass / 0 fail** | `flake-main.txt` |
| CI unit+integration on `87bce41` | **success** | `ci-receipts.txt` |

Label: **flake-suspect** (order/state dependent). Raw logs kept; the test was not modified. Filed as its own Pod-line card.

## Review gap — found, fixed, re-verified

Cycle 1 returned the PARTIAL because (a) the flake split was asserted in prose with no attached logs, and (b) the reviewer cannot open the PR (Developer bridge not connected), so CI was unverifiable from the card. Fix: attached the three standalone runs, a `suite-summary.txt` carrying the failing assertion (the reviewer could not reach the tail of a 26 K log), and `ci-receipts.txt` read from the Actions API. Re-roll → 7/7 MET.

## Deploy verification (merged ≠ served)

After the merge the founders' box was brought to clean `main`: the tree's uncommitted local patch (the same fix) was dropped, `main` checked out at `e0ace62`, the API rebuilt and both services restarted. Verified: `/health` 200, `ts.net:8446` 200, substrate config reads `{provider: 'deepseek', model: 'deepseek-chat'}`.

**Flagged:** the shared tree had been sitting on `wip/optimus/pod-factory-ready` (2 commits ahead of main — **intact**, nothing lost). A serving checkout and run worktrees must not share one working tree; that branch's work needs its own worktree.

## Verification notes

- Assertions read the substrate's **effective** config (persisted `config.json`, else the in-memory config the stub holds), so the pre-fix early return fails as a value mismatch rather than an ENOENT.
- Provider activity is seeded through the real `writeIntegrationConfig` path (codex `authenticated: true`; openai `api_key`), not a mocked resolver.
- `clearProviderEnv()` was read to confirm it does not clear `DEEPSEEK_API_KEY` (it clears ANTHROPIC/OPENAI/OPENROUTER only) — the fallback depends on that.
- Operator-lane implementation (12-line change, unambiguous contract); the reviewer lane is unchanged and blind.
- Provenance: the fix is the patch proven live on the founders' box during the run-011 deploy; input patch + sha256 `09eab01d…` attached to the card.

## Remaining risks

- None identified. The fallback is inert whenever a managed provider is active.
- Not in this run: surfacing the fallback in Connections/Capabilities (spec open question, accepted silent for v1).

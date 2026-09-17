# Run-012 — evidence

- **Card**: `N9zHVtucPsjsx9RthfOkIyDT` (Pod Factory) — IN PROGRESS since 16:22Z
- **Branch / head**: `factory/fix-smartware-deepseek-fallback` @ `87bce41`
- **Base**: `origin/main` `ccba1fb`
- **Worktree**: `/opt/data/dev-workspaces/worktrees/pod-run012`
- **Outcome**: _pending — PR + review + founder gate_

## Checks

| Check | Command | Result |
| --- | --- | --- |
| RED first (pre-fix) | `node --test dist/test/smartware-llm-config.test.js` on `ccba1fb` | **2 fail / 4 pass** — `provider: 'none'` vs expected `'deepseek'` (`evidence/red-first.txt`) |
| Targeted GREEN (post-fix) | same file, `87bce41` | **6/6 pass** (`evidence/green-targeted.txt`) |
| Typecheck | `npm run typecheck` | see `evidence/typecheck.txt` |
| Design lint | `npm run lint:design` | see `evidence/design-lint.txt` |
| UI unit tests | `npm run test:ui` | see `evidence/ui-tests.txt` |
| Build | `npm run build` | see `evidence/build.txt` |
| Backend suite | `node --test dist/test/**/*.test.js` | see `evidence/test-full.txt` |
| Guard scan | `bash scripts/guard-scan.sh <worktree> origin/main` | **clean, 2 changed files, no findings** (`evidence/guard-scan.txt`) |
| CI (PR) | Beta gate + E2E on the head sha | _pending_ |

## Changed files

- `src/services/ai-provider.ts` (+12 / −2) — DeepSeek fallback in `syncSmartwareLLMConfig`.
- `src/test/smartware-llm-config.test.ts` (+128) — 6 cases: fallback default model · `DEEPSEEK_MODEL` honoured · no key stays `none` · codex never replaced · active provider wins · idempotent re-run.

## Provenance

The fix is the patch proven live on the founders' box during the run-011 deploy (working tree, uncommitted there); this run makes it a reviewed change on `main`. Input patch + sha256: `uploads/run012/ai-provider-deepseek-fallback.patch` (`09eab01d…`) — attached to the card as an artifact.

## Verification notes

- Assertions read the substrate's **effective** config (persisted `config.json`, else the in-memory config the stub holds), so the pre-fix early return fails as a value mismatch rather than an ENOENT.
- Provider activity is seeded through the real `writeIntegrationConfig` path (codex `authenticated: true`; openai `api_key`), not a mocked resolver.
- `clearProviderEnv()` was read to confirm it does not clear `DEEPSEEK_API_KEY` (it clears ANTHROPIC/OPENAI/OPENROUTER only) — the fallback depends on that.
- Operator-lane implementation (12-line change, unambiguous contract); the reviewer lane is unchanged and blind.

## Flake receipts (ours-vs-pre-existing split)

Full suite on the branch: **1 failure, not ours** — `dist/test/pod-flow.test.js` → `/pod/query returns the matching claim instead of an unrelated high-confidence sibling` (`assert.ok(deadlineVersion)` undefined). Nothing in this diff touches retrieval, claims, or the pod-flow surface (2 files: `src/services/ai-provider.ts`, `src/test/smartware-llm-config.test.ts`).

| Run | Result | Log |
| --- | --- | --- |
| Full suite, branch `87bce41` | 1 fail (the pod-flow claim test) | `evidence/test-full.txt` |
| Standalone on the branch, run 1 | **11 pass / 0 fail** | `evidence/flake-branch-run1.txt` |
| Standalone on the branch, run 2 | **11 pass / 0 fail** | `evidence/flake-branch-run2.txt` |
| Standalone on clean `main` (`ccba1fb`) | **11 pass / 0 fail** | `evidence/flake-main.txt` |

Label: **flake-suspect** (order/state dependent). Both raw logs kept; the test was not modified. CI's suite run on the PR is the authoritative second full-suite pass.

## Remaining risks


- None identified beyond review. The fallback is inert whenever a managed provider is active.
- Not in this run: surfacing the fallback in Connections/Capabilities (spec open question, accepted silent for v1).

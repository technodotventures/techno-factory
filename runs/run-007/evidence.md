# Run 007 — evidence (Capabilities UI improvements I1–I9)

> Mission check: *did this actually happen?* Every claim maps to a test result, a file, a screenshot, or a CI run.

- **Work item:** card `redacted-id-25` (10 criteria) — commissioned by the founder ("fix them all").
- **PR:** `technodotventures/pod#8` — branch `factory/feat-capabilities-ui`, from `origin/main` @ `c9889ae`.
- **Commit:** `603aa8a` (7 files, +638/−19).

## Local gates (Node 26.5.1 — the repo's verified runtime)

| gate | result |
|---|---|
| typecheck (server + ui) | ✅ clean |
| unit — backend (`npm test`) | ✅ **290/290** (incl. both slow watch-auth tests) |
| unit — ui (`npm run test:ui`, new — tsx runner) | ✅ **93/93**, incl. the new `capability-utils` suite (7 tests) |
| e2e (cockpit + a11y + visual) | ✅ **17/17** — a11y zero-critical on all six surfaces; visual baselines unchanged |
| guard scan (vs `c9889ae`) | ✅ 7 files; one expected flag: UI-impacting → design check at Review |

## Live evidence (seeded isolated instance — `/tmp/pod-run007`, ports 8961/5391)

Seed: Skill r1 approved → r2 draft (`SKILL.md` rewritten + `reference/cheatsheet.md` added); Plugin r1 approved → r2 draft (MCP alpha removed / beta added; Skill added).

| shot | shows |
|---|---|
| `01-inbox-cards.png` | freshness strip ("Last updated…") + card chips: `2m ago` · `3 files` · `Trust: blocked` · `Update waiting` |
| `02-skill-review-panel.png` / `02b-…fullpage` | "Proposed by person-local"; **WHAT CHANGED**: `± SKILL.md` · `+ reference/cheatsheet.md`; revision history r2 DRAFT / r1 APPROVED |
| `02c-local-files-not-materialized.png` | "**Not materialized** — Canonical revision retained in Pod…" (the F2 fix, previously a false "Directory found") |
| `03-library-filters.png` | filter bar (search + source/time/update/deployment selects) + chips (`In Library` · `2 files` · `Not deployed`) |
| `04-library-skills-subview.png` | "Skills — 1 in Library" sub-view, plugin hidden |
| `05-plugin-diff.png` | `MCP beta added` · `MCP alpha removed` · `SKILL extra added` (true diff vs retained revision) |
| `06-discover-freshness.png` | "last loaded 04:30 PM; sources may be cached up to 5 minutes" + per-source health: "SkillsMP unreachable" |

## Review fix (2026-09-15) — footer chips overflowed the tile

Founder review of the uploaded screenshots caught a real defect the gates missed: the card footer was a nowrap flex row, so the new chips spilled **outside the card** (measured: up to ~250px past the right edge; `Trust: blocked` / `Not deployed` rendered over the neighbouring column).

- **Fix (`80a6a45`):** `.skill-tile-footer { flex-wrap: wrap; }` + nowrap for the status/update badges. Re-measured: every chip `insideX/insideY = true`; tiles grow to fit (250px). Refreshed shots below.
- **Why the gates missed it:** the e2e kit runs **empty states** (no seeded cards with full chip rows); visual baselines cover activity/docs/connections only; a11y is orthogonal to overflow; and the run-003 audit predates the chips. The manual screenshot check verified *presence*, not *containment* — corrected now.
- **Regression guard added:** `e2e/capabilities.spec.ts` seeds a skill through r1→r2 and asserts geometrically that every footer chip stays within the tile box — this class cannot ship silently again.
- **Found while re-running:** the cockpit journal assertion pinned a **daily-rotating** prompt string (`CURATED_PROMPTS`); it would have failed CI from Sep 15 onward regardless. Anchored to the stable prompt-card structure instead.

Full local e2e after fixes: **18/18** (includes the new guard).

- **Tag + compatibility filters omitted** — no data exists for those dimensions today; documented in the PR rather than faked with dead controls.
- **F9 unsupported-target note** verified in code; a live repro needs a connected agent without a codex/claude harness (none existed in the instance) — flagged in the PR.
- **CI (PR #8):** `verify` ✅ **5m13s** (beta gate — incl. the new `test:ui` step) · `e2e` ✅ **4m16s** (cockpit + a11y + visual). Runs: [34869502397](https://github.com/technodotventures/pod/actions/runs/34869502397) · [34869502340](https://github.com/technodotventures/pod/actions/runs/34869502340).

---

**Merged (Sep 16 2026, 14:03:10Z):** squash `0e592fe` via [pod#8](https://github.com/technodotventures/pod/pull/8), final head `de3c319` (conflict resolution vs the design-lint merge: cockpit journal spec → main's stable-chrome test; `beta:gate` combines `lint:design` + `test:ui`). Checks on the final head: `verify` ✅ · `e2e` ✅. Card → COMPLETE with 10/10 criteria ticked. Merge path: one-off per founder instruction (checks verified via the Actions API; token lacks `Checks:Read`).

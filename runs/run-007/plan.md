# Run 007 — plan (Capabilities UI improvements I1–I9)

- **Work item:** card `redacted-id-25` — "Pod capabilities UI 007 — implement audit improvements (I1–I9)" (IN PROGRESS).
- **Source of record:** run-003 audit (`runs/run-003/audit.md`; card `redacted-id-23`). Founder commissioned the full set ("fix them all", chat, Sep 14).
- **Repo / branch:** `technodotventures/pod` · `factory/feat-capabilities-ui` (from `origin/main` @ `c9889ae`). Worktree: `pod-run007`.
- **Scope:** capability-view UI changes + two *additive* server response fields (skillssh cache metadata for I1b; agent `harness` for I9). No stored revision/deployment state changes.
- **Finding → improvement map:** F1→I1a/I1b · F2→I2 · F3→I3 · F4→I4 · F5→I5 · F6→I6 · F7→I7 · F8→I8 · F9→I9.

## Design-principles mapping (agentic UX standard, `docs/design-principles.md`)

- **Confidence gradient** — freshness disclosure (I1) + card freshness chips (I5): certainty visible, quiet when fresh, explicit when cached/stale.
- **Scope boundary** — deploy-target handling (I9) states plainly what Pod can and cannot materialize for an agent.
- **Intervention points** — review panels (I3/I4/I8) now disclose what changed and who proposed it before approve/reject.

## Test plan

1. New unit suite: `ui/test/capability-utils.test.ts` (file/component diff, instruction classification, freshness buckets).
2. Existing suites stay green: typecheck (`npm run build`), full `npm test`, E2E (cockpit/a11y/visual).
3. Visual baselines regenerated for the changed capabilities surfaces (expected change, not masked).
4. a11y: zero critical violations on all nav surfaces (existing gate).

## Evidence plan

Live pass on an isolated instance (`/tmp/pod-run007`, ports 8961/5391) seeded with: a Skill (r1 approved → r2 draft: rewritten `SKILL.md` + added resource) and a Plugin (r1 approved → r2 draft: MCP removed/added + Skill added). Screenshots → `runs/run-007/evidence/` + card artifacts:

- `01-inbox-cards.png` — freshness strip + card chips (freshness, files, trust, deploy).
- `02…` skill review — What changed (instruction/resource split), Proposed by, Not materialized.
- `03/04` — Library filter bar + Skills sub-view.
- `05` — plugin component diff.
- `06` — Discover freshness strip + per-source health line.

## Out of scope

Source adapters, IA redesign, brand work; automated fixes beyond proposals (per audit §6). Tag/compatibility filters omitted where no data exists (documented in the PR).

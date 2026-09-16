# Run 008 — design lint on Pod (@shadcn/lint) — evidence

**Card:** `redacted-id-21` (Techno OS board) · **PR:** `technodotventures/pod#10` · **Branch:** `factory/feat-design-lint`
**Status:** IN REVIEW (Sep 15, 2026)

## Receipts

- **Red-first**: `evidence/lint-red-01.txt` — 211 errors, incl. the Button arbitrary values (`h-[34px]`, `px-[18px]`, `rounded-[10px]`, `size-[26px]`…).
- **Green**: `evidence/lint-final-02.txt` — **0 errors** / 261 warnings (all `no-raw-colors` on inline-SVG literals; warn-scoped, non-blocking).
- **Gates**: `gates-typecheck.txt` (exit 0) · `gates-unit.txt` (**290 pass / 0 fail**) · `gates-ui-build.txt` (exit 0) · `gates-lint-design.txt` (0 errors).
- **Visual**: `button-spot-check.png` — sizes 34/28/40/34/26 px, icon radii 12/8 px, pill radii intact (rendered against the compiled CSS).
- **Checklist ids**: `checklist-ids.json` — 8 criteria; **all 8 ticked** (CI criterion ticked on fix-commit run 2).

## What shipped (PR #10)

- `.oxlintrc.json` scoped rules v0 + narrow reasoned allowlist; oxlint + @shadcn/lint pinned (1.83.0 / 0.1.0).
- Fixes: Button on-scale swaps; `accent` → `accent-ui` tokens (select/badge/dropdown/dialog); dead-class cleanup (orphaned `animate-*` cluster, `ai-chat-open`, `endorsement-modal*`, legacy view hooks); state-marker emissions guarded.
- Wiring: `npm run lint` = typecheck + `lint:design`; beta gate runs it; `AGENTS.md` + `docs/testing.md`.

## Follow-ups / findings

- `no-raw-colors` SVG-literal pass (~181 literal `fill`/`stroke` values; needs design decisions: `currentColor` vs theme vars).
- `DESIGN.md` referenced by config note + AGENTS.md — ships via a parallel PR.
- `no-restyle` component contracts — later increment.
- Finding filed (`redacted-id-22`): native Planner Spec runs don't create checklist items (2/2 runs, silent) — operator instantiated criteria meanwhile.
- Mechanic learned: `PostTaskComment` blocks — paragraph blocks need `id`s (same as document blocks); image blocks from uploads embed as-is.

## Fix cycle (CI e2e red → green)

- **CI run 1** (`34952723318`): verify ✅ / e2e ❌ — two failures: (1) `ai-chat-open` removed by the cleanup — it is the e2e-asserted *state signal* for the Ask Pod panel (regression; restored + allow-listed as a documented marker; audit of all other removed classes found no other consumers); (2) journal surface spec hardcoded one day's curated prompt — `CURATED_PROMPTS[hash(date) % 12]` rotates daily in no-provider envs (pre-existing time bomb; main fails it on any re-run that day too). Fixed spec asserts surface chrome instead.
- **Local verification**: cockpit suite **8/8 green** incl. both fixed tests (`run008-e2e-full.log`), lint 0 errors.
- **Fix commit** `f72dc65` → **CI run 2**: verify ✅ / e2e ✅ — criterion 7 ticked; **8/8 on the card**.
- CI failure log kept: `pod10-e2e-log.txt`.

## Closeout (Sep 15)

- **Merged:** founder "Approved" comment (11:23:59Z, human — no `via_app`) → merge-approved worker rails all PASS → squash-merge with `--match-head-commit`: merge commit `4b1fc94e3f727d00ab3420b90e122a1f77eb89ae`. Receipt comment posted on the card; card moved **IN REVIEW → COMPLETE** (activity id 116197).
- **R4 hardened** (post-merge): approval candidates must be human-posted (`via_app` and `posted_by_agent` both absent) — agent-authored comments (e.g. a Planner note containing "merge it") previously matched the approve regex; now ignored and reported under "agent-authored ignored".
- **Gap noted:** nothing yet *watches* for approvals — the worker is invoked manually today (operator). Target: approval comment auto-triggers the worker (workflow lane).



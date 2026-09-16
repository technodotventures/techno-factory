# Run 004 — evidence (Pod E2E test kit: Playwright + a11y + visual + CI)

> Mission check: *did this actually happen?* Every claim below maps to a file in `evidence/` or a link.

- **Work item:** card `redacted-id-27` — criteria written by the native **Factory Planner** (13 items — see `plan.md`)
- **Repo / branch:** `technodotventures/pod` · `factory/feat-e2e-kit` (from `origin/main` @ `9c24f86`; final head `86cc82c`)
- **PR:** `technodotventures/pod#5` — <https://github.com/technodotventures/pod/pull/5>
- **CI:** `e2e` workflow **green** — 4m8s, `17 passed (38.0s)`, report artifact (<https://github.com/technodotventures/pod/actions/runs/34833462887>). `verify` (beta gate) red — **pre-existing repo-wide** (npm audit advisories, nodemailer family; red on main since POD-AUDIT-003 and on PR #4 too). Candidate follow-up run: clear the audit.
- **Merged:** `daf7219` — PR #5 merged Sep 14 12:22Z; post-merge `e2e` on `main` green (4m24s, run `34843032302`). Kit now lives in `main`.

## Evidence map

| Criterion | Evidence |
|---|---|
| 1. Red→green (video+traces) | `red-a11y-log.txt` (first suite run: 5/15 failed incl. 18 critical axe findings) + deliberate-regression demo — `red-mutation-video.mp4` / `.webm`, `red-mutation-screenshot.png`, `red-mutation-context.md` (onboarding text mutated → suite failed with video + trace; reverted → green) |
| 2. Deps + chromium | `package.json`: `@playwright/test@^1.63.0`, `@axe-core/playwright@^4.13.0`; `npx playwright install chromium` verified |
| 3. Boots real Pod, isolated | `playwright.config.ts` webServer: `rm -rf .e2e-data && npm run dev:all` (API 8907 / UI 5273); green: `green-full-suite.txt` |
| 4. Onboarding journey | `e2e/onboarding.setup.ts` — wizard → "Set up later" → cockpit (passes) |
| 5. Safe interaction, no external calls | `e2e/cockpit.spec.ts` — Ask Pod toggle + input; external requests blocked and asserted empty (passes) |
| 6. Six surfaces render | `e2e/cockpit.spec.ts` — one test per surface (passes) |
| 7. a11y zero critical | `e2e/a11y.spec.ts` — six surfaces (passes after the fixes; `red-a11y-log.txt` = before state) |
| 8. Visual baselines | `e2e/visual.spec.ts` + 3 committed PNG baselines; clean-run reproduction (passes) |
| 9. CI | `.github/workflows/e2e.yml` — run link at close |
| 10. Guard scan | `guard-scan.txt` — 3 findings, all justified: lockfile (new devDeps) · binaries (visual baselines, intentional) · UI files (aria-label additions only; no visual delta — design check N/A) |
| 11. Artifacts on card | card comment + files (red/green logs, mutation video + screenshot) |
| 12. Docs | `docs/testing.md` + README pointer (in PR diff) |

## Real findings (fixed in-run)

The new gate caught **8 real critical a11y defects** on its first run — icon-only buttons without accessible names (Ask Pod close, Docs create-chevron, theme segments ×3) and unlabeled checkboxes (select-all + rows). Fixed with `aria-label`s only; no visual change; listed in the PR.

## Notes

- Deterministic by design: fresh `.e2e-data/` per invocation; onboarding exercised every run; single worker (shared live Pod).
- Total suite time ~59s local; ~16 files / 391 insertions.
- Cost: $0 tooling (Playwright + axe-core OSS); CI minutes within plan.

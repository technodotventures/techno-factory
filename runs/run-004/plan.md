# Run 004 — plan (Pod E2E test kit: Playwright + a11y + visual + CI)

- **Work item:** card `redacted-id-27` — "Pod E2E 004 — Playwright test kit (journeys, a11y, visual, CI)" (criteria written by the native **Factory Planner**; card created Sep 14, moved IN PROGRESS at run start).
- **Repo:** `technodotventures/pod` · **Branch:** `factory/feat-e2e-kit` (from `origin/main` @ `9c24f86`)
- **Risk tier:** R0/R1 (test infrastructure only; no application behavior change — one additive dev-port override in `vite.config.ts`).
- **Why:** make the test story a strength (user ask): E2E journeys, a11y gate, visual baselines, CI — all free tooling; feeds the factory's Test station evidence contract (`docs/templates/test-plan.md`).

## Acceptance criteria (from the card — authoritative, written by the Factory Planner)

1. First proof: a Playwright journey exists that starts with a failing assertion against the cockpit surface and passes only after the suite is wired up (video+traces record the red state).
2. `npm install` adds Playwright + @axe-core/playwright + @playwright/test as devDependencies and chromium is installable via the standard install command.
3. An e2e script boots a real local Pod via `npm run dev:all` with an isolated data dir, on chromium, and the suite passes against it.
4. Journey: first-run onboarding (skip path) lands on the cockpit with no manual steps.
5. One safe interaction is tested: opening a panel succeeds and makes no external network calls (mocked/blocked and asserted).
6. All six nav surfaces — Activity, Memory, Docs, Journal, Capabilities, Connections — render when navigated to.
7. Accessibility: axe-core scan reports zero critical violations on each cockpit nav surface.
8. Visual snapshots: committed baselines exist (`--update-snapshots` on first run) and the snapshot suite passes on a clean run.
9. GitHub Actions workflow (ubuntu) runs unit tests then E2E, uploads report artifacts (HTML report, video, traces), and is green on the PR.
10. Evidence: red→green is captured — a deliberate-failure demo produces video + traces, then passes after the fix.
11. Guard scan is clean, or every finding is justified in writing on the card.
12. Artifacts (report, video, traces, screenshots) are attached/linked on the card.
13. Docs describe how to run the suite locally (isolated data dir, chromium) and in CI (workflow + artifact locations).

## Approach

- `playwright.config.ts` at repo root: chromium project; `webServer` boots the paired dev stack (`npm run dev:all`) with an **isolated data dir + dedicated ports** (`COFFEE_POD_PORT`, `COFFEE_POD_UI_PORT`, `COFFEE_POD_DATA_DIR`, empty token); traces/videos on failure.
- `e2e/` specs: first-run onboarding → cockpit (setup project); six nav surfaces; safe interaction (Ask Pod panel open/close); axe-core scan (zero critical); visual snapshots (committed baselines, diff tolerance).
- Small `vite.config.ts` addition: `COFFEE_POD_UI_PORT` override (default stays 5173) so parallel/E2E runs get deterministic ports.
- `.github/workflows/e2e.yml` (ubuntu-latest, node 26): `npm ci` → `playwright install --with-deps chromium` → unit tests → E2E → upload `playwright-report/` + traces.
- `.gitignore`: `test-results/`, `playwright-report/`, `data/` artifacts.

## Out of scope

UI redesign; Electron/desktop tests; cross-browser beyond chromium (v1); external integrations (Google/registry calls stay mocked or unclicked); Coffee-side changes.

## Evidence plan

red→green (deliberate mutation demo recorded — failing test captured with video+trace, then reverted green) · full suite output · axe report · visual baselines diff check · guard-scan verdict on the diff · CI run link · recordings uploaded to the card.

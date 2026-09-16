# Test plan — <run id>

> Per-run contract for the **Test** station. Blind: the Tester never sees the Builder's reasoning. Every acceptance criterion maps to evidence; verdicts go on the card (pass / fail / waived + reason). **A criterion without evidence does not pass** (`pdlc.md`).

## 1. Criteria → tests

| Criterion (card checklist) | Layer | Test / command | Evidence |
|---|---|---|---|
| <criterion> | unit · integration · E2E · visual · a11y · manual | <test id or command> | <red→green output · video · trace · report> |

## 2. Layers (standard kit — all free)

- **Unit + integration** — the repo's own runner (e.g. `npm test`), invoked via the repo's scripts. Failures reported as failures.
- **E2E — Playwright** — the journey list; **RED capture first** (record the failing run), then GREEN. Video + trace on failure.
- **Visual** — Playwright screenshot assertions vs committed baselines. No external service at v1.
- **Layout containment** — seeded worst-case content through the real API; assert every chip/badge/child stays inside its container (`child.right <= container.right + 1`; same for bottom) and no page overflow (`documentElement.scrollWidth`). Empty-state suites never count; screenshot *presence* is not containment (precedent: pod `e2e/capabilities.spec.ts` — footer chips spilled past tile edges while every empty-state suite stayed green).
- **Design lint (Tailwind repos)** — `@shadcn/lint`: off-token arbitrary values, undeclared colors, unknown/dead classes; errors carry the fix. Clean before Review; intentional custom classes get `@utility` declarations or scoped ignores.
- **Accessibility** — `@axe-core/playwright`: zero critical violations.
- **Guards** — `scripts/guard-scan.sh` clean (secrets, forbidden refs, UI-change flag → design verdict).
- **Perf (when in scope)** — Lighthouse CI budget on the touched surfaces.

A layer may be skipped only with a written reason on the card.

## 3. Flake policy

One retry, trace captured on retry; a second failure is a real failure. Quarantine only with a filed card + named owner. No silent reruns — a rerun without a note is indistinguishable from a fake pass.

## 4. Environment

Fresh worktree (the repo's worktree helper); per-run ports + seed data; deterministic seed, fixed timezone; no shared state between concurrent runs.

## 5. Evidence package

Upload to the card: per-criterion verdict summary · recordings (`kind: recording`) · failing output / trace · CI run link. **Silence never passes.**

# Run 005 — plan (Pod deps: clear the beta-gate audit red)

- **Work item:** card `redacted-id-26` — "Pod deps 005 — clear the beta-gate: dependency advisories" (criteria by the native **Factory Planner**)
- **Repo / branch:** `technodotventures/pod` · `factory/fix-deps-audit` (from `origin/main` @ `48f5adf` — i.e. after run 002's merge)
- **Risk tier:** R0 — lockfile-only dependency refresh; zero source changes.
- **Why:** `npm audit --audit-level=low` fails on 5 advisories (nodemailer family) → the beta-gate `verify` check is red repo-wide since POD-AUDIT-003 (main, PR #4, PR #5).

## Approach

`npm audit fix` (semver-safe): imapflow 1.4.7 → 1.7.8, mailparser 3.9.14 → 3.9.26 (pulls nodemailer 10.0.9). Lockfile-only; `package.json` ranges untouched.

## Evidence plan

red audit (exit 1, 5 vulns) → fix → green audit (exit 0, 0 vulns) · typecheck clean · full suite 290/290 · e2e 17/17 · guard-scan (lockfile churn = the change itself) · `verify` + `e2e` green on the PR.

## Out of scope

Source changes; broader dependency modernization; anything Coffee-side.

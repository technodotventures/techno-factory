# Containment guard — mutation test (RED proof) · 2026-09-15

**Claim proven:** the e2e containment guard (`e2e/capabilities.spec.ts` — "capability card chips stay within the tile") fails on the pre-fix CSS — it is mutation-sensitive to the exact defect class the founder caught in run 007 (footer chips spilling past tile edges).

**Method:** reverted `ui/src/styles.css` to `80a6a45~1` (pre-fix: footer without `flex-wrap`) in the run-007 worktree; ran `npx playwright test e2e/capabilities.spec.ts` against the broken CSS.

**Result (RED):**
- `Error: chip 3 overflows the tile's right edge`
- `Expected: <= 493 · Received: 495.8125` (assertion at `e2e/capabilities.spec.ts:76`)
- Exit 1 — 1 failed / 1 passed (onboarding setup), 18.3s.

**Restore:** fixed CSS restored (`git checkout --`); worktree clean. GREEN on the same spec is CI-proven on PR #8 (`verify` + `e2e` SUCCESS, head of `factory/feat-capabilities-ui`).

Artifacts: `containment-red-proof.log`, `containment-red-chip-overflow.png`.

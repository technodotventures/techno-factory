# Run 000 — plan (POD-AUDIT-003)

- **Work item:** POD-AUDIT-003 (Pod audit, 2026-08-24) — `/pod/watch` authorizes the request but trusts the caller-supplied `actor_id` to select the subscription identity.
- **Repo:** `technodotventures/pod` · **Branch:** `factory/fix-watch-actor-binding` · **Base:** `e4630df`
- **Risk tier:** R3 (security-sensitive) — human Review gate mandatory; Adversary station not yet built (accepted limitation for run 0, noted).
- **Run type:** seed run 0 — first manual pass of the loop (plan → build → test → evidence → review).

## Acceptance criteria

1. Strict mode: an unauthenticated watch upgrade is refused (401). *(first proof step)*
2. A wrong bearer token is refused (401).
3. The owner's real api token connects (regression).
4. An agent token claiming a different actor — including the owner — is refused (403).
5. An agent token claiming itself connects, with its own grant (regression).
6. Open mode (no api token, no PIN): unauthenticated local watch still connects (documented parity with GET routes).
7. Full test suite green (incl. new tests); typecheck clean.
8. `docs/FINDINGS.md` + audit index updated (`POD-AUDIT-003 → fixed`).
9. Guard scan clean (mechanical diff integrity).

## First proof step (red before green)

Write the upgrade test **first**: in the current code, an anonymous upgrade claiming the owner's `actor_id` connects (101) and receives the owner's event stream. Capture that failing run; then fix; then the same request is refused (401/403) while legitimate paths still connect. Both runs kept as evidence.

## Approach

- Mirror the HTTP auth cascade (`security/auth.ts`) for the raw upgrade path: owner api token → client token → PIN session → agent bearer, plus the identity-binding rule from `requireActorAuth` (owner/session may act for any actor; client/agent only for their own).
- Keep `evaluateAccess` as defense-in-depth (unchanged); keep trust-mode semantics as documented (open / local-trust reads stay unauthenticated).
- New test file boots the app and drives real upgrade requests via a raw HTTP client — first upgrade-path tests in the repo.

## Surfaces / files

- `src/routes/watch.ts` — modified (auth function + wiring)
- `src/test/watch-auth.test.ts` — new
- `docs/FINDINGS.md`, `docs/audits/2026-08-24-pod-audit.md` — status updates

## Risks & blast radius

- `local-trust` reads remain unauthenticated by design — flagged, out of scope to change.
- Raw-socket error responses carry reason phrases, not JSON bodies (parity with existing handler style).
- Test boot is slow in this environment (~60s/app); fine for a regression file, noted for future optimization.

## Out of scope

- POD-AUDIT-002 (agent token hashing) · trust-mode semantics · watch protocol/frames · UI · anything outside `/pod/watch` auth.

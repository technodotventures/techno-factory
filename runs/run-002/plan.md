# Run 002 — plan (Pod audit 002: hash agent bearer tokens at rest)

- **Work item:** card `redacted-id-28` — "Pod audit 002 — hash agent bearer tokens at rest" (criteria written by the native **Factory Planner**; card created 14:22Z, moved IN PROGRESS at run start).
- **Repo:** `technodotventures/pod` · **Branch:** `factory/fix-agent-token-hashing` (from `origin/main` @ `9c24f86`)
- **Risk tier:** R1 (server-internal storage; auth path touched, no production deploy).

## Acceptance criteria (from the card — authoritative, written by the Factory Planner)

1. First proof step (must FAIL before, PASS after): a test asserts that after creating an agent token no column in the SQLite token row contains the plaintext `cpod_agent_*` value.
2. Issuance returns the plaintext token to the caller **exactly once** and stores only a hash — unrecoverable afterwards.
3. A valid plaintext token authenticates by hashing the presented value and matching the stored hash.
4. A wrong or unknown token is rejected with the same auth failure as before (acceptance set unchanged).
5. Migration converts every existing plaintext row to its hash; a pre-migration token still authenticates.
6. After migration, a query for rows whose value starts with `cpod_agent_` returns zero rows.
7. The migration is safe to run twice (second run: nothing to convert, no error).
8. Hash scheme matches the client-token scheme.
9. Automated test on create / authenticate / migrate paths passes, output attached to the card.
10. Existing client-token behavior unchanged (their tests still pass).

## Approach

`src/pod/db.ts` — sha256-hex at rest in `agents.auth_token`; `getAgentByToken` hashes before lookup; mint paths (`upsertAgent` back-fill/create, `rotateAgentToken`) store hashes and return the raw value once; `rowToAgent` never surfaces stored values. Open-time migration rewrites legacy plaintext rows in place (idempotent by prefix check). Route updates: connection `?reveal=1` rotates (raw unrecoverable ⇒ reveal must mint); spawn rotates for existing children. New test `src/test/agent-token-hash.test.ts`; `harness-adapters.test.ts` update assertion adapted to the new contract.

## Out of scope

Pod UI/desktop display changes; token expiry policy; anything Coffee-side.

# Run 001 — plan (MCP token helper)

- **Work item:** card `M1s37GjeuV3PkJv3HpiUkjus` — "Coffee MCP helper: auto-refresh expired tokens" (criteria written by the native Factory Planner; card moved to IN PROGRESS at run start).
- **Repo:** `technodotventures/techno-factory` · **Branch:** `factory/coffee-mcp-token-helper`
- **Risk tier:** R1 (tooling, no production surface).

## Acceptance criteria (from the card — authoritative)

1. A shared Python helper loads the token store and returns a valid access token.
2. ~60s remaining → refreshes before the call.
3. After a single 401: refresh once, retry once; second failure returns — no loop.
4. `coffee-notify` uses the shared helper instead of duplicating token logic.
5. Automated tests cover proactive refresh / 401 retry / refresh failure / no-infinite-retry.
6. No token values in logs, errors, or test output.
7. Refreshed token persisted with 0600 (atomic).
8. *(optional)* Docs state location/config and how scripts call the helper.
9. *(optional)* A representative round-trip script uses the helper.

## First proof step

`cd scripts && python3 -m unittest test_coffee_mcp` fails before the module exists (ModuleNotFoundError), passes after — red run captured, then green.

## Approach

`scripts/coffee_mcp.py` — dependency-free module: `get_token()` (proactive refresh at ≤60s), `mcp_call()` (single refresh-and-retry on 401), atomic 0600 persist, secrets never in errors, injectable opener/clock for deterministic tests. `coffee-notify` refactored to import it. Tests: stdlib `unittest`, no new dependencies.

## Out of scope

Coffee-side changes; multi-account stores; the webhook pipeline.

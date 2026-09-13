# Run 001 — evidence package

- **Work item:** "Coffee MCP helper: auto-refresh expired tokens" (card `M1s37GjeuV3PkJv3HpiUkjus`)
- **Branch:** `factory/coffee-mcp-token-helper` · **Repo:** `technodotventures/techno-factory`
- **Status:** tests green — PR link prepared (one founder click; token lacks PRs:write). Review gate pending.

## Changed files

| File | Δ |
|---|---|
| `scripts/coffee_mcp.py` | new — shared client: `get_token()` (≤60s proactive refresh), `mcp_call()` (one refresh-and-retry on 401, never a loop), atomic 0600 persist, secret-free errors |
| `scripts/test_coffee_mcp.py` | new — 9 unit tests (stdlib unittest, no new deps) covering all card criteria paths |
| `scripts/coffee-notify` | refactored onto the shared helper — token logic removed (was duplicated) |

## Checks

| Check | Result | Evidence |
|---|---|---|
| Red run (tests before module) | ✖ `ModuleNotFoundError` — as expected | `red-coffee-mcp.txt` |
| Green run (9 unit tests) | ✅ 9/9 OK | `green-coffee-mcp.txt` |
| Live integration — refactored `coffee-notify` post | ✅ posted to the "Techno OS" channel | `coffee-notify-live.txt` |
| Guard scan | ✅ see scan output | `guard-scan.txt` |

## Notes

- One test was corrected during the cycle: a missing token store cannot refresh (no `refresh_token` to present) — the honest behavior is a clean `CoffeeAuthError` pointing at the consent flow, asserted as such.
- Optional criteria delivered: the module docstring documents store location/config/usage; live round-trip proof above.

## Replay fields

- commands: `cd scripts && python3 -m unittest test_coffee_mcp -v` · `python3 scripts/coffee-notify "<msg>"` · `scripts/guard-scan.sh <repo> origin/main`

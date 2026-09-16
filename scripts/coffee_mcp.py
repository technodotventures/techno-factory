#!/usr/bin/env python3
"""coffee_mcp — shared Coffee MCP client with transparent token refresh.

Every factory script that talks to Coffee uses this module instead of
re-implementing token loading/refresh:

    from coffee_mcp import get_token, mcp_call

    token = get_token()                      # refreshes when <=60s remain
    result = mcp_call("GetTask", {"workspace": "techno", "task_hash": "..."})
                                             # one refresh-and-retry on 401

Configuration (env overrides):
    COFFEE_TOKEN_STORE  token store path   (default ~/mcp-tokens/meetcoffee.client.json)
    COFFEE_OAUTH_JSON   client credentials (default ~/coffee_oauth_factory.json)
    COFFEE_MCP_URL      MCP endpoint       (default https://meetcoffee.ai/api/mcp)

Guarantees:
    - Tokens are the ONLY thing persisted, atomic write + mode 0600.
    - Access tokens expire after ~30 min; refresh tokens rotate on use.
    - Exactly one refresh-and-retry for a 401, never a loop.
    - No token value ever appears in logs or raised errors.

Run tests:  cd scripts && python3 -m unittest test_coffee_mcp -v
"""
import json
import os
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_TOKEN_STORE = os.environ.get("COFFEE_TOKEN_STORE", os.path.expanduser("~/mcp-tokens/meetcoffee.client.json"))
DEFAULT_OAUTH_JSON = os.environ.get("COFFEE_OAUTH_JSON", os.path.expanduser("~/coffee_oauth_factory.json"))
MCP_URL = os.environ.get("COFFEE_MCP_URL", "https://meetcoffee.ai/api/mcp")
REFRESH_SKEW_SECONDS = 60

# Cloudflare on meetcoffee.ai rejects bare library user agents.
_USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
               "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")


class CoffeeAuthError(RuntimeError):
    """Token-store or refresh failure. Never embeds token values."""


class CoffeeMcpError(RuntimeError):
    """MCP call failure. Never embeds token values."""


def _default_opener(request, timeout=60):
    return urllib.request.urlopen(request, timeout=timeout)


def _now():
    return time.time()


def _load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _save_json_atomic(path, data):
    directory = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp_path = tempfile.mkstemp(prefix=".coffee-tokens-", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
        os.chmod(tmp_path, 0o600)
        os.replace(tmp_path, path)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def refresh_token(*, store_path=DEFAULT_TOKEN_STORE, oauth_path=DEFAULT_OAUTH_JSON,
                  opener=None, now=None):
    """Perform the refresh_token grant and persist the new token atomically."""
    opener = opener or _default_opener
    now = now or _now

    try:
        store = _load_json(store_path)
    except FileNotFoundError:
        raise CoffeeAuthError("token store not found — run the OAuth consent flow first") from None
    except ValueError:
        raise CoffeeAuthError("token store is not valid JSON") from None
    try:
        client = _load_json(oauth_path)
    except (FileNotFoundError, ValueError):
        raise CoffeeAuthError("OAuth client configuration not found or invalid") from None

    body = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": store.get("refresh_token", ""),
        "client_id": client["client_id"],
        "client_secret": client["client_secret"],
    }).encode()
    request = urllib.request.Request(client["token_endpoint"], data=body, headers={
        "User-Agent": _USER_AGENT, "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://meetcoffee.ai", "Referer": "https://meetcoffee.ai/",
    })
    try:
        response = json.loads(opener(request).read().decode())
    except urllib.error.HTTPError as error:
        raise CoffeeAuthError(f"token refresh rejected (HTTP {error.code})") from None
    except Exception as error:  # network error or invalid JSON
        raise CoffeeAuthError(f"token refresh failed ({type(error).__name__})") from None

    if not isinstance(response, dict) or not response.get("access_token"):
        raise CoffeeAuthError("token refresh response missing access_token")

    updated = {
        "client_id": store.get("client_id", client.get("client_id")),
        "resource": store.get("resource", "https://meetcoffee.ai/api/mcp"),
        "scope": response.get("scope", store.get("scope")),
        "access_token": response["access_token"],
        "expires_in": response.get("expires_in", 1800),
        "refresh_token": response.get("refresh_token") or store.get("refresh_token"),
        "token_type": response.get("token_type", "Bearer"),
        "obtained_at": now(),
    }
    _save_json_atomic(store_path, updated)
    return updated


def get_token(*, force=False, store_path=DEFAULT_TOKEN_STORE, oauth_path=DEFAULT_OAUTH_JSON,
              opener=None, now=None):
    """Return a valid access token, refreshing proactively when needed."""
    now = now or _now
    try:
        store = _load_json(store_path)
    except (FileNotFoundError, ValueError):
        store = {}
    expires_at = float(store.get("obtained_at") or 0) + float(store.get("expires_in") or 0)
    if force or not store.get("access_token") or expires_at - now() <= REFRESH_SKEW_SECONDS:
        store = refresh_token(store_path=store_path, oauth_path=oauth_path, opener=opener, now=now)
    return store["access_token"]


def _parse_response(raw):
    """MCP responses are JSON or SSE; both wrap the JSON-RPC envelope."""
    try:
        return json.loads(raw)
    except ValueError:
        pass
    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith("data:"):
            try:
                return json.loads(line[5:].strip())
            except ValueError:
                continue
    raise CoffeeMcpError("mcp response was not valid JSON")


def mcp_call(tool_name, arguments, *, request_id=None, store_path=DEFAULT_TOKEN_STORE,
             oauth_path=DEFAULT_OAUTH_JSON, opener=None, now=None):
    """Call a Coffee MCP tool. One refresh-and-retry on 401; never a loop."""
    opener = opener or _default_opener
    now = now or _now

    def attempt(access_token):
        request = urllib.request.Request(MCP_URL, data=json.dumps({
            "jsonrpc": "2.0", "id": request_id or 1, "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }).encode(), headers={
            "User-Agent": _USER_AGENT, "Authorization": "Bearer " + access_token,
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
        })
        return _parse_response(opener(request).read().decode())

    token = get_token(store_path=store_path, oauth_path=oauth_path, opener=opener, now=now)
    try:
        return attempt(token)
    except urllib.error.HTTPError as error:
        if error.code != 401:
            raise CoffeeMcpError(f"mcp call failed (HTTP {error.code})") from None

    # The access token was rejected: refresh once, retry once.
    token = get_token(force=True, store_path=store_path, oauth_path=oauth_path, opener=opener, now=now)
    try:
        return attempt(token)
    except urllib.error.HTTPError as error:
        raise CoffeeMcpError(f"mcp call failed (HTTP {error.code})") from None


if __name__ == "__main__":
    # Quick self-check: prints workspace count without touching store contents.
    result = mcp_call("ListMyWorkspaces", {})
    payload = result.get("result", {}) if isinstance(result, dict) else {}
    print("coffee_mcp self-check ok:", "ListMyWorkspaces" in json.dumps(result))

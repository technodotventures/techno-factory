"""Red-first tests for scripts/coffee_mcp.py — the shared Coffee MCP client
with transparent token refresh (run 001, card redacted-id-19).

Run:  cd scripts && python3 -m unittest test_coffee_mcp -v
"""
import io
import json
import os
import stat
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coffee_mcp  # noqa: E402


class FakeResponse:
    def __init__(self, payload, status=200):
        self._body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.status = status

    def read(self):
        return self._body


def http_error(code):
    return urllib.error.HTTPError("https://example.test", code, "err", {}, io.BytesIO(b"{}"))


class Recorder:
    """Fake opener: records calls, returns queued responses or raises queued errors."""

    def __init__(self, queue):
        self.queue = list(queue)
        self.calls = []

    def __call__(self, req, timeout=60):
        body = req.data.decode() if getattr(req, "data", None) else None
        self.calls.append({
            "url": req.full_url,
            "headers": {k.lower(): v for k, v in req.headers.items()},
            "body": body,
        })
        item = self.queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def make_oauth(path):
    with open(path, "w") as f:
        json.dump({
            "client_id": "client-123",
            "client_secret": "secret-abc",
            "token_endpoint": "https://coffee.test/oauth/code",
        }, f)
    return path


def make_store(path, obtained_at, expires_in, access="old-access", refresh="old-refresh"):
    with open(path, "w") as f:
        json.dump({
            "client_id": "client-123", "resource": "https://meetcoffee.ai/api/mcp",
            "scope": "coffeeConnect.workspace.all", "access_token": access,
            "expires_in": expires_in, "refresh_token": refresh,
            "token_type": "Bearer", "obtained_at": obtained_at,
        }, f)
    return path


TOKEN_RESPONSE = {
    "access_token": "new-access-token",
    "expires_in": 1800,
    "refresh_token": "new-refresh-token",
    "scope": "coffeeConnect.workspace.all",
    "token_type": "Bearer",
}


class TokenRefreshTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="coffee-mcp-test-")
        self.store = os.path.join(self.dir, "tokens.json")
        self.oauth = make_oauth(os.path.join(self.dir, "oauth.json"))
        self.now = 1_000_000.0

    def cfg(self, opener, now=None):
        return dict(store_path=self.store, oauth_path=self.oauth,
                    opener=opener, now=now or (lambda: self.now))

    def test_fresh_token_is_used_without_refresh(self):
        make_store(self.store, obtained_at=self.now - 10, expires_in=1800)
        rec = Recorder([])
        tok = coffee_mcp.get_token(**self.cfg(rec))
        self.assertEqual(tok, "old-access")
        self.assertEqual(len(rec.calls), 0, "no network call expected for a fresh token")

    def test_expiring_token_is_refreshed_and_persisted_0600(self):
        make_store(self.store, obtained_at=self.now - 1795, expires_in=1800)  # 5s left < 60s skew
        rec = Recorder([FakeResponse(TOKEN_RESPONSE)])
        tok = coffee_mcp.get_token(**self.cfg(rec))
        self.assertEqual(tok, "new-access-token")
        self.assertEqual(len(rec.calls), 1)
        # refresh grant correctness
        body = urllib.parse.parse_qs(rec.calls[0]["body"])
        self.assertEqual(body["grant_type"], ["refresh_token"])
        self.assertEqual(body["refresh_token"], ["old-refresh"])
        # persisted atomically, mode 0600, rotated refresh token
        with open(self.store) as f:
            saved = json.load(f)
        self.assertEqual(saved["access_token"], "new-access-token")
        self.assertEqual(saved["refresh_token"], "new-refresh-token")
        mode = stat.S_IMODE(os.stat(self.store).st_mode)
        self.assertEqual(mode, 0o600)

    def test_refresh_keeps_old_refresh_token_if_not_rotated(self):
        make_store(self.store, obtained_at=self.now - 1799, expires_in=1800)
        resp = dict(TOKEN_RESPONSE)
        resp.pop("refresh_token")
        rec = Recorder([FakeResponse(resp)])
        coffee_mcp.get_token(**self.cfg(rec))
        with open(self.store) as f:
            saved = json.load(f)
        self.assertEqual(saved["refresh_token"], "old-refresh")

    def test_refresh_failure_raises_clean_error_without_secrets(self):
        make_store(self.store, obtained_at=self.now - 1799, expires_in=1800)
        rec = Recorder([http_error(400)])
        with self.assertRaises(coffee_mcp.CoffeeAuthError) as ctx:
            coffee_mcp.get_token(**self.cfg(rec))
        msg = str(ctx.exception)
        self.assertNotIn("old-access", msg)
        self.assertNotIn("old-refresh", msg)
        self.assertNotIn("secret-abc", msg)

    def test_missing_token_store_raises_clean_auth_error(self):
        # No store = no refresh_token to present; the honest behavior is a
        # clean error pointing at the consent flow — never a silent network call.
        rec = Recorder([FakeResponse(TOKEN_RESPONSE)])
        with self.assertRaises(coffee_mcp.CoffeeAuthError) as ctx:
            coffee_mcp.get_token(**self.cfg(rec))
        self.assertIn("token store", str(ctx.exception))
        self.assertEqual(len(rec.calls), 0, "no network call when there is nothing to refresh with")


class McpCallTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="coffee-mcp-test-")
        self.store = os.path.join(self.dir, "tokens.json")
        self.oauth = make_oauth(os.path.join(self.dir, "oauth.json"))
        self.now = 1_000_000.0
        make_store(self.store, obtained_at=self.now - 10, expires_in=1800)

    def cfg(self, opener):
        return dict(store_path=self.store, oauth_path=self.oauth,
                    opener=opener, now=(lambda: self.now))

    def ok_payload(self):
        return {"jsonrpc": "2.0", "id": 1, "result": {"content": [{"type": "text", "text": "{\"success\": true}"}]}}

    def test_successful_call_single_attempt(self):
        rec = Recorder([FakeResponse(self.ok_payload())])
        out = coffee_mcp.mcp_call("GetTask", {"workspace": "techno"}, **self.cfg(rec))
        self.assertEqual(len(rec.calls), 1)
        self.assertTrue(json.dumps(out))

    def test_401_triggers_one_refresh_and_one_retry(self):
        rec = Recorder([http_error(401), FakeResponse(TOKEN_RESPONSE), FakeResponse(self.ok_payload())])
        out = coffee_mcp.mcp_call("GetTask", {"workspace": "techno"}, **self.cfg(rec))
        kinds = [c["url"] for c in rec.calls]
        self.assertEqual(len(rec.calls), 3, f"expected call, refresh, retry — got {kinds}")
        self.assertIn("oauth/code", rec.calls[1]["url"])
        self.assertEqual(rec.calls[2]["headers"].get("authorization"), "Bearer new-access-token")
        self.assertTrue(json.dumps(out))

    def test_401_twice_returns_error_without_retry_loop(self):
        rec = Recorder([http_error(401), FakeResponse(TOKEN_RESPONSE), http_error(401)])
        with self.assertRaises(coffee_mcp.CoffeeMcpError) as ctx:
            coffee_mcp.mcp_call("GetTask", {"workspace": "techno"}, **self.cfg(rec))
        self.assertEqual(len(rec.calls), 3, "exactly one refresh + one retry, never more")
        self.assertIn("401", str(ctx.exception))
        self.assertNotIn("new-access-token", str(ctx.exception))

    def test_non_401_error_is_not_retried(self):
        rec = Recorder([http_error(500)])
        with self.assertRaises(coffee_mcp.CoffeeMcpError):
            coffee_mcp.mcp_call("GetTask", {"workspace": "techno"}, **self.cfg(rec))
        self.assertEqual(len(rec.calls), 1)


if __name__ == "__main__":
    unittest.main()

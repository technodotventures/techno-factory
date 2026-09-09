# Factory Work API v0

## Work submission

`POST /v1/work`

```json
{
  "organizationId": "techno-ventures",
  "workspaceId": "protocols",
  "projectId": "smartware",
  "threadId": "coffee-thread-42",
  "actorId": "founder",
  "agentId": "founder-agent",
  "origin": "coffee",
  "correlationId": "corr-001",
  "idempotencyKey": "idem-001",
  "riskTier": "R2",
  "title": "Add revocation conformance case",
  "objective": "Produce a draft test artifact.",
  "budget": {
    "maxTokens": 20000,
    "maxWallSeconds": 900
  }
}
```

A first submission returns `201` with `{ "created": true, "work": ... }`. A retry with the same authenticated client, organisation, idempotency key, and identical payload returns `200` with the original work item and `created: false`. Reusing the key with a different payload returns `409`.

## Read routes

- `GET /v1/work/:workId`
- `GET /v1/work/:workId/events`
- `GET /health` — unauthenticated readiness only

Project grants are enforced on submission and reads. An unauthorised caller receives `403`; unknown work within an authorised scope receives `404`.

## HMAC authentication

Authenticated HTTP requests require:

- `x-factory-key-id`
- `x-factory-timestamp` — Unix seconds
- `x-factory-nonce` — unique within the acceptance window
- `x-factory-signature` — lowercase hexadecimal HMAC-SHA256

The canonical signing payload is:

```text
UPPERCASE_METHOD
PATH_WITH_QUERY
TIMESTAMP
NONCE
SHA256_HEX_OF_EXACT_BODY_BYTES
```

The server:

1. rejects missing or unknown key IDs;
2. rejects timestamps outside the configured five-minute window;
3. compares signatures in constant time;
4. persists consumed nonces in SQLite so replay protection survives process restarts;
5. resolves the key to a client grant;
6. independently enforces organisation, workspace, project, and permission scope.

HMAC credentials are a bootstrap service-to-service mechanism. Production Coffee integration should move to short-lived workload identity or OAuth where Coffee's actual capabilities support it; the authorisation grant and application contract remain unchanged.

## MCP adapter

`createFactoryMcpServer` exposes:

- `submit_work`
- `get_work`
- `list_work_events`

The MCP transport/authentication layer binds one validated client grant when constructing the server. Tool arguments cannot choose or expand that grant. All tools call the same `WorkService` used by HTTP.

A remote Streamable HTTP transport is the intended Coffee-facing MCP deployment. Its OAuth/service-identity details remain deliberately outside v0 until Coffee's actual agent invitation contract is inspected.

## Risk tiers

- `R0`: read-only research and ingestion
- `R1`: proposals, experiment design, sandbox evaluation
- `R2`: bounded draft code/spec artifacts
- `R3`: dependencies, migrations, compatibility, security/privacy-sensitive changes
- `R4`: merge, release, deployment, credentials, infrastructure, or governance

Risk tier is recorded now; enforcement gates beyond project scope are the next policy-engine slice.

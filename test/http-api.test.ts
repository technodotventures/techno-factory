import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import type { FastifyInstance } from "fastify";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { WorkService } from "../src/application/work-service.js";
import {
  HmacAuthenticator,
  MemoryReplayStore,
  signRequest,
} from "../src/infrastructure/hmac-auth.js";
import { SqliteWorkStore } from "../src/infrastructure/sqlite-work-store.js";
import { buildHttpApi } from "../src/transport/http-api.js";

const secret = "test-secret-that-is-at-least-32-bytes-long";
const keyId = "coffee-test";
const timestamp = "1787376000";
const submission = {
  organizationId: "techno-ventures",
  workspaceId: "protocols",
  projectId: "smartware",
  threadId: "coffee-thread-42",
  actorId: "stevie",
  agentId: "tech-head",
  origin: "coffee",
  correlationId: "corr-001",
  idempotencyKey: "idem-001",
  riskTier: "R2",
  title: "Add revocation conformance case",
  objective: "Produce a draft test artifact for Smartware revocation behaviour.",
  budget: { maxTokens: 20_000, maxWallSeconds: 900 },
} as const;

function signedHeaders(
  body: string,
  nonce = "nonce-001",
  method = "POST",
  path = "/v1/work",
) {
  return {
    ...(body ? { "content-type": "application/json" } : {}),
    "x-factory-key-id": keyId,
    "x-factory-timestamp": timestamp,
    "x-factory-nonce": nonce,
    "x-factory-signature": signRequest({
      secret,
      method,
      path,
      timestamp,
      nonce,
      body,
    }),
  };
}

describe("HTTP work API", () => {
  let directory: string;
  let store: SqliteWorkStore;
  let app: FastifyInstance;

  beforeEach(async () => {
    directory = await mkdtemp(join(tmpdir(), "techno-factory-http-"));
    store = new SqliteWorkStore(join(directory, "factory.db"));
    const authenticator = new HmacAuthenticator({
      credentials: [
        {
          keyId,
          secret,
          grant: {
            clientId: "coffee-test",
            organizationId: "techno-ventures",
            workspaceId: "protocols",
            projectIds: ["smartware"],
            permissions: ["work:submit", "work:read"],
          },
        },
      ],
      replayStore: new MemoryReplayStore(),
      now: () => 1_787_376_000_000,
    });
    app = buildHttpApi({
      workService: new WorkService(store, {
        createId: () => "work-001",
        now: () => "2026-08-22T05:20:00.000Z",
      }),
      authenticator,
    });
    await app.ready();
  });

  afterEach(async () => {
    await app.close();
    store.close();
    await rm(directory, { recursive: true, force: true });
  });

  it("reports readiness without exposing authenticated state", async () => {
    const response = await app.inject({ method: "GET", url: "/health" });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({ status: "ok" });
  });

  it("accepts a signed project-scoped work request", async () => {
    const body = JSON.stringify(submission);
    const response = await app.inject({
      method: "POST",
      url: "/v1/work",
      headers: signedHeaders(body),
      payload: body,
    });

    expect(response.statusCode).toBe(201);
    expect(response.json()).toMatchObject({
      created: true,
      work: { id: "work-001", projectId: "smartware", status: "accepted" },
    });
  });

  it("returns accepted work and its audit events", async () => {
    const body = JSON.stringify(submission);
    await app.inject({
      method: "POST",
      url: "/v1/work",
      headers: signedHeaders(body, "nonce-create"),
      payload: body,
    });

    const workPath = "/v1/work/work-001";
    const workResponse = await app.inject({
      method: "GET",
      url: workPath,
      headers: signedHeaders("", "nonce-get", "GET", workPath),
    });
    const eventsPath = `${workPath}/events`;
    const eventsResponse = await app.inject({
      method: "GET",
      url: eventsPath,
      headers: signedHeaders("", "nonce-events", "GET", eventsPath),
    });

    expect(workResponse.statusCode).toBe(200);
    expect(workResponse.json()).toMatchObject({ id: "work-001", status: "accepted" });
    expect(eventsResponse.statusCode).toBe(200);
    expect(eventsResponse.json()).toMatchObject({
      events: [{ workId: "work-001", type: "work.accepted" }],
    });
  });

  it("rejects a tampered request signature", async () => {
    const body = JSON.stringify(submission);
    const headers = signedHeaders(body, "nonce-tampered");
    headers["x-factory-signature"] = "00".repeat(32);

    const response = await app.inject({
      method: "POST",
      url: "/v1/work",
      headers,
      payload: body,
    });

    expect(response.statusCode).toBe(401);
    expect(response.json()).toEqual({ error: "authentication_failed" });
  });

  it("rejects nonce replay but permits an idempotent retry with a fresh nonce", async () => {
    const body = JSON.stringify(submission);
    const firstHeaders = signedHeaders(body, "nonce-retry");
    const first = await app.inject({
      method: "POST",
      url: "/v1/work",
      headers: firstHeaders,
      payload: body,
    });
    const replay = await app.inject({
      method: "POST",
      url: "/v1/work",
      headers: firstHeaders,
      payload: body,
    });
    const retry = await app.inject({
      method: "POST",
      url: "/v1/work",
      headers: signedHeaders(body, "nonce-retry-fresh"),
      payload: body,
    });

    expect(first.statusCode).toBe(201);
    expect(replay.statusCode).toBe(401);
    expect(retry.statusCode).toBe(200);
    expect(retry.json()).toMatchObject({ created: false, work: { id: "work-001" } });
  });

  it("rejects work outside the authenticated project grant", async () => {
    const body = JSON.stringify({ ...submission, projectId: "expresso" });
    const response = await app.inject({
      method: "POST",
      url: "/v1/work",
      headers: signedHeaders(body, "nonce-project-denied"),
      payload: body,
    });

    expect(response.statusCode).toBe(403);
    expect(response.json()).toEqual({ error: "forbidden" });
  });
});

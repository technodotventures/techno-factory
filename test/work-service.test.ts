import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { WorkService } from "../src/application/work-service.js";
import { AuthorizationError, IdempotencyConflictError } from "../src/domain/errors.js";
import { SqliteWorkStore } from "../src/infrastructure/sqlite-work-store.js";
import type { WorkSubmission } from "../src/domain/work.js";

const submission: WorkSubmission = {
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
  budget: {
    maxTokens: 20_000,
    maxWallSeconds: 900,
  },
};

const grant = {
  clientId: "coffee-production",
  organizationId: "techno-ventures",
  workspaceId: "protocols",
  projectIds: ["smartware"],
  permissions: ["work:submit", "work:read"],
} as const;

describe("WorkService submission", () => {
  let directory: string;
  let store: SqliteWorkStore;

  beforeEach(async () => {
    directory = await mkdtemp(join(tmpdir(), "techno-factory-"));
    store = new SqliteWorkStore(join(directory, "factory.db"));
  });

  afterEach(async () => {
    store.close();
    await rm(directory, { recursive: true, force: true });
  });

  it("reuses the existing work item when a request is retried", () => {
    const service = new WorkService(store, {
      createId: () => "work-001",
      now: () => "2026-08-22T05:15:00.000Z",
    });

    const first = service.submit(submission, grant);
    const retry = service.submit(submission, grant);

    expect(first.created).toBe(true);
    expect(retry.created).toBe(false);
    expect(retry.work.id).toBe(first.work.id);
    expect(store.listEvents(first.work.id)).toHaveLength(1);
  });

  it("rejects reuse of an idempotency key with different work", () => {
    const service = new WorkService(store, {
      createId: () => "work-001",
      now: () => "2026-08-22T05:15:00.000Z",
    });
    service.submit(submission, grant);

    expect(() =>
      service.submit({ ...submission, objective: "A conflicting objective." }, grant),
    ).toThrow(IdempotencyConflictError);
  });

  it("rejects submission outside the client's project grant", () => {
    const service = new WorkService(store);

    expect(() =>
      service.submit({ ...submission, projectId: "expresso" }, grant),
    ).toThrow(AuthorizationError);
  });

  it("reads persisted work after the store is reopened", () => {
    const databasePath = join(directory, "factory.db");
    const service = new WorkService(store, {
      createId: () => "work-001",
      now: () => "2026-08-22T05:15:00.000Z",
    });
    service.submit(submission, grant);
    store.close();

    store = new SqliteWorkStore(databasePath);
    const reopenedService = new WorkService(store);

    expect(reopenedService.get("work-001", grant).objective).toBe(submission.objective);
    expect(reopenedService.listEvents("work-001", grant)).toHaveLength(1);
  });
});

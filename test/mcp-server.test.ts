import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { WorkService } from "../src/application/work-service.js";
import { SqliteWorkStore } from "../src/infrastructure/sqlite-work-store.js";
import { createFactoryMcpServer } from "../src/transport/mcp-server.js";

const grant = {
  clientId: "coffee-mcp",
  organizationId: "techno-ventures",
  workspaceId: "protocols",
  projectIds: ["smartware"],
  permissions: ["work:submit", "work:read"],
} as const;

const submission = {
  organizationId: "techno-ventures",
  workspaceId: "protocols",
  projectId: "smartware",
  threadId: "coffee-thread-42",
  actorId: "stevie",
  agentId: "tech-head",
  origin: "coffee",
  correlationId: "corr-mcp-001",
  idempotencyKey: "idem-mcp-001",
  riskTier: "R2",
  title: "Draft MCP conformance proposal",
  objective: "Create a project-scoped factory work item through MCP.",
  budget: { maxTokens: 10_000, maxWallSeconds: 600 },
} as const;

describe("factory MCP adapter", () => {
  let directory: string;
  let store: SqliteWorkStore;
  let client: Client;
  let server: ReturnType<typeof createFactoryMcpServer>;

  beforeEach(async () => {
    directory = await mkdtemp(join(tmpdir(), "techno-factory-mcp-"));
    store = new SqliteWorkStore(join(directory, "factory.db"));
    const workService = new WorkService(store, {
      createId: () => "work-mcp-001",
      now: () => "2026-08-22T05:25:00.000Z",
    });
    server = createFactoryMcpServer({ workService, grant });
    client = new Client({ name: "factory-test-client", version: "0.1.0" });
    const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
    await Promise.all([
      server.connect(serverTransport),
      client.connect(clientTransport),
    ]);
  });

  afterEach(async () => {
    await client.close();
    await server.close();
    store.close();
    await rm(directory, { recursive: true, force: true });
  });

  it("submits work through the same application service used by HTTP", async () => {
    const response = await client.callTool({
      name: "submit_work",
      arguments: submission,
    });

    expect(response.isError).not.toBe(true);
    expect(response.structuredContent).toMatchObject({
      created: true,
      work: { id: "work-mcp-001", projectId: "smartware" },
    });
    expect(store.getById("work-mcp-001")).toMatchObject({
      id: "work-mcp-001",
      origin: "coffee",
    });
  });

  it("reads work and events through project-scoped tools", async () => {
    await client.callTool({ name: "submit_work", arguments: submission });

    const work = await client.callTool({
      name: "get_work",
      arguments: { workId: "work-mcp-001" },
    });
    const events = await client.callTool({
      name: "list_work_events",
      arguments: { workId: "work-mcp-001" },
    });

    expect(work.isError).not.toBe(true);
    expect(work.structuredContent).toMatchObject({
      work: { id: "work-mcp-001", status: "accepted" },
    });
    expect(events.isError).not.toBe(true);
    expect(events.structuredContent).toMatchObject({
      events: [{ type: "work.accepted", workId: "work-mcp-001" }],
    });
  });
});

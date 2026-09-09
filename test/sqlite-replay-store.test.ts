import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { SqliteReplayStore } from "../src/infrastructure/sqlite-replay-store.js";

describe("SqliteReplayStore", () => {
  it("rejects a nonce after the process-level store is reopened", async () => {
    const directory = await mkdtemp(join(tmpdir(), "techno-factory-replay-"));
    const databasePath = join(directory, "factory.db");

    let store = new SqliteReplayStore(databasePath);
    expect(store.consume("coffee", "nonce-001", 10_000, 1_000)).toBe(true);
    store.close();

    store = new SqliteReplayStore(databasePath);
    expect(store.consume("coffee", "nonce-001", 10_000, 2_000)).toBe(false);
    store.close();
    await rm(directory, { recursive: true, force: true });
  });
});

import { DatabaseSync } from "node:sqlite";

import type { WorkStore, StoredWork } from "../application/work-store.js";
import { WorkEventSchema, WorkItemSchema, type WorkEvent, type WorkItem } from "../domain/work-item.js";

interface WorkRow {
  payload_json: string;
  fingerprint: string;
}

interface EventRow {
  payload_json: string;
}

export class SqliteWorkStore implements WorkStore {
  private readonly database: DatabaseSync;

  constructor(path: string) {
    this.database = new DatabaseSync(path, {
      enableForeignKeyConstraints: true,
      enableDoubleQuotedStringLiterals: false,
    });
    this.database.exec("PRAGMA journal_mode = WAL; PRAGMA synchronous = FULL;");
    this.database.exec(`
      CREATE TABLE IF NOT EXISTS work_items (
        id TEXT PRIMARY KEY,
        client_id TEXT NOT NULL,
        organization_id TEXT NOT NULL,
        workspace_id TEXT NOT NULL,
        project_id TEXT NOT NULL,
        idempotency_key TEXT NOT NULL,
        fingerprint TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE (client_id, organization_id, idempotency_key)
      ) STRICT;

      CREATE TABLE IF NOT EXISTS work_events (
        id TEXT PRIMARY KEY,
        work_id TEXT NOT NULL REFERENCES work_items(id) ON DELETE CASCADE,
        type TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        created_at TEXT NOT NULL
      ) STRICT;

      CREATE INDEX IF NOT EXISTS idx_work_events_work_created
        ON work_events(work_id, created_at, id);
    `);
  }

  findByIdempotency(
    clientId: string,
    organizationId: string,
    idempotencyKey: string,
  ): StoredWork | undefined {
    const row = this.database
      .prepare(
        `SELECT payload_json, fingerprint
         FROM work_items
         WHERE client_id = ? AND organization_id = ? AND idempotency_key = ?`,
      )
      .get(clientId, organizationId, idempotencyKey) as WorkRow | undefined;

    if (!row) return undefined;
    return {
      work: WorkItemSchema.parse(JSON.parse(row.payload_json)),
      fingerprint: row.fingerprint,
    };
  }

  insert(work: WorkItem, event: WorkEvent, clientId: string, fingerprint: string): void {
    this.database.exec("BEGIN IMMEDIATE");
    try {
      this.database
        .prepare(
          `INSERT INTO work_items (
             id, client_id, organization_id, workspace_id, project_id,
             idempotency_key, fingerprint, payload_json, created_at
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        )
        .run(
          work.id,
          clientId,
          work.organizationId,
          work.workspaceId,
          work.projectId,
          work.idempotencyKey,
          fingerprint,
          JSON.stringify(work),
          work.createdAt,
        );
      this.database
        .prepare(
          `INSERT INTO work_events (id, work_id, type, payload_json, created_at)
           VALUES (?, ?, ?, ?, ?)`,
        )
        .run(event.id, event.workId, event.type, JSON.stringify(event), event.createdAt);
      this.database.exec("COMMIT");
    } catch (error) {
      this.database.exec("ROLLBACK");
      throw error;
    }
  }

  getById(id: string): WorkItem | undefined {
    const row = this.database
      .prepare("SELECT payload_json FROM work_items WHERE id = ?")
      .get(id) as Pick<WorkRow, "payload_json"> | undefined;
    return row ? WorkItemSchema.parse(JSON.parse(row.payload_json)) : undefined;
  }

  listEvents(workId: string): WorkEvent[] {
    const rows = this.database
      .prepare(
        `SELECT payload_json FROM work_events
         WHERE work_id = ? ORDER BY created_at ASC, id ASC`,
      )
      .all(workId) as unknown as EventRow[];
    return rows.map((row) => WorkEventSchema.parse(JSON.parse(row.payload_json)));
  }

  close(): void {
    this.database.close();
  }
}

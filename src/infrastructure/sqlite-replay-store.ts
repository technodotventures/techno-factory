import { DatabaseSync } from "node:sqlite";

import type { ReplayStore } from "./hmac-auth.js";

export class SqliteReplayStore implements ReplayStore {
  private readonly database: DatabaseSync;

  constructor(path: string) {
    this.database = new DatabaseSync(path, {
      enableForeignKeyConstraints: true,
      enableDoubleQuotedStringLiterals: false,
    });
    this.database.exec("PRAGMA journal_mode = WAL; PRAGMA synchronous = FULL;");
    this.database.exec(`
      CREATE TABLE IF NOT EXISTS request_nonces (
        key_id TEXT NOT NULL,
        nonce TEXT NOT NULL,
        expires_at_ms INTEGER NOT NULL,
        PRIMARY KEY (key_id, nonce)
      ) STRICT;
      CREATE INDEX IF NOT EXISTS idx_request_nonces_expiry
        ON request_nonces(expires_at_ms);
    `);
  }

  consume(keyId: string, nonce: string, expiresAtMs: number, nowMs: number): boolean {
    this.database.exec("BEGIN IMMEDIATE");
    try {
      this.database
        .prepare("DELETE FROM request_nonces WHERE expires_at_ms <= ?")
        .run(nowMs);
      const result = this.database
        .prepare(
          `INSERT OR IGNORE INTO request_nonces (key_id, nonce, expires_at_ms)
           VALUES (?, ?, ?)`,
        )
        .run(keyId, nonce, expiresAtMs);
      this.database.exec("COMMIT");
      return result.changes === 1;
    } catch (error) {
      this.database.exec("ROLLBACK");
      throw error;
    }
  }

  close(): void {
    this.database.close();
  }
}

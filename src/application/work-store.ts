import type { WorkEvent, WorkItem } from "../domain/work-item.js";

export interface StoredWork {
  work: WorkItem;
  fingerprint: string;
}

export interface WorkStore {
  findByIdempotency(
    clientId: string,
    organizationId: string,
    idempotencyKey: string,
  ): StoredWork | undefined;
  insert(work: WorkItem, event: WorkEvent, clientId: string, fingerprint: string): void;
  getById(id: string): WorkItem | undefined;
  listEvents(workId: string): WorkEvent[];
  close(): void;
}

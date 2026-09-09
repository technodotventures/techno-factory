import { createHash, randomUUID } from "node:crypto";

import { ClientGrantSchema, type ClientGrant, type ClientPermission } from "../domain/client-grant.js";
import { AuthorizationError, IdempotencyConflictError, WorkNotFoundError } from "../domain/errors.js";
import type { WorkEvent, WorkItem } from "../domain/work-item.js";
import { WorkSubmissionSchema, type WorkSubmission } from "../domain/work.js";
import type { WorkStore } from "./work-store.js";

export interface WorkServiceDependencies {
  createId: () => string;
  now: () => string;
}

export interface SubmitResult {
  work: WorkItem;
  created: boolean;
}

const defaultDependencies: WorkServiceDependencies = {
  createId: () => randomUUID(),
  now: () => new Date().toISOString(),
};

function fingerprint(submission: WorkSubmission): string {
  return createHash("sha256").update(JSON.stringify(submission)).digest("hex");
}

function requirePermission(grant: ClientGrant, permission: ClientPermission): void {
  if (!grant.permissions.includes(permission)) {
    throw new AuthorizationError(`Client ${grant.clientId} lacks ${permission}`);
  }
}

function authorizeSubmission(submission: WorkSubmission, grant: ClientGrant): void {
  requirePermission(grant, "work:submit");
  if (
    submission.organizationId !== grant.organizationId ||
    submission.workspaceId !== grant.workspaceId ||
    !grant.projectIds.includes(submission.projectId)
  ) {
    throw new AuthorizationError("Submission is outside the client grant");
  }
}

export class WorkService {
  constructor(
    private readonly store: WorkStore,
    private readonly dependencies: WorkServiceDependencies = defaultDependencies,
  ) {}

  submit(input: unknown, rawGrant: unknown): SubmitResult {
    const submission = WorkSubmissionSchema.parse(input);
    const grant = ClientGrantSchema.parse(rawGrant);
    authorizeSubmission(submission, grant);

    const submissionFingerprint = fingerprint(submission);
    const existing = this.store.findByIdempotency(
      grant.clientId,
      submission.organizationId,
      submission.idempotencyKey,
    );

    if (existing) {
      if (existing.fingerprint !== submissionFingerprint) {
        throw new IdempotencyConflictError(
          "Idempotency key was already used for a different submission",
        );
      }
      return { work: existing.work, created: false };
    }

    const timestamp = this.dependencies.now();
    const work: WorkItem = {
      ...submission,
      id: this.dependencies.createId(),
      status: "accepted",
      createdAt: timestamp,
      updatedAt: timestamp,
    };
    const event: WorkEvent = {
      id: `${work.id}:accepted`,
      workId: work.id,
      type: "work.accepted",
      createdAt: timestamp,
      actorId: work.actorId,
      origin: work.origin,
    };

    this.store.insert(work, event, grant.clientId, submissionFingerprint);
    return { work, created: true };
  }

  get(workId: string, rawGrant: unknown): WorkItem {
    const grant = ClientGrantSchema.parse(rawGrant);
    requirePermission(grant, "work:read");
    const work = this.store.getById(workId);
    if (!work) {
      throw new WorkNotFoundError(`Work item ${workId} was not found`);
    }
    if (
      work.organizationId !== grant.organizationId ||
      work.workspaceId !== grant.workspaceId ||
      !grant.projectIds.includes(work.projectId)
    ) {
      throw new AuthorizationError("Work item is outside the client grant");
    }
    return work;
  }

  listEvents(workId: string, rawGrant: unknown): WorkEvent[] {
    this.get(workId, rawGrant);
    return this.store.listEvents(workId);
  }
}

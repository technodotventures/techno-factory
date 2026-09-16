import { describe, expect, it } from "vitest";

import { WorkSubmissionSchema } from "../src/domain/work.js";

const validSubmission = {
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
} as const;

describe("WorkSubmissionSchema", () => {
  it("accepts a complete project-scoped submission", () => {
    const parsed = WorkSubmissionSchema.parse(validSubmission);

    expect(parsed).toEqual(validSubmission);
  });

  it("rejects a submission without an idempotency key", () => {
    const { idempotencyKey: _removed, ...incomplete } = validSubmission;

    expect(() => WorkSubmissionSchema.parse(incomplete)).toThrow();
  });
});

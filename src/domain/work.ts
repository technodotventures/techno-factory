import { z } from "zod";

const identifier = z.string().trim().min(1).max(200);

export const WorkOriginSchema = z.enum([
  "coffee",
  "personal-hermes",
  "factory",
]);

export const RiskTierSchema = z.enum(["R0", "R1", "R2", "R3", "R4"]);

export const WorkBudgetSchema = z
  .object({
    maxTokens: z.number().int().positive().max(10_000_000),
    maxWallSeconds: z.number().int().positive().max(86_400),
  })
  .strict();

export const WorkSubmissionSchema = z
  .object({
    organizationId: identifier,
    workspaceId: identifier,
    projectId: identifier,
    threadId: identifier,
    actorId: identifier,
    agentId: identifier,
    origin: WorkOriginSchema,
    correlationId: identifier,
    idempotencyKey: identifier,
    riskTier: RiskTierSchema,
    title: z.string().trim().min(1).max(240),
    objective: z.string().trim().min(1).max(10_000),
    budget: WorkBudgetSchema,
  })
  .strict();

export type WorkSubmission = z.infer<typeof WorkSubmissionSchema>;
export type WorkOrigin = z.infer<typeof WorkOriginSchema>;
export type RiskTier = z.infer<typeof RiskTierSchema>;

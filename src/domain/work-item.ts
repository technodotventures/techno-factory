import { z } from "zod";

import { WorkSubmissionSchema } from "./work.js";

export const WorkStatusSchema = z.enum([
  "accepted",
  "running",
  "blocked",
  "completed",
  "cancelled",
  "failed",
]);

export const WorkItemSchema = WorkSubmissionSchema.extend({
  id: z.string().min(1),
  status: WorkStatusSchema,
  createdAt: z.iso.datetime(),
  updatedAt: z.iso.datetime(),
});

export const WorkEventSchema = z.object({
  id: z.string().min(1),
  workId: z.string().min(1),
  type: z.enum(["work.accepted"]),
  createdAt: z.iso.datetime(),
  actorId: z.string().min(1),
  origin: z.string().min(1),
});

export type WorkItem = z.infer<typeof WorkItemSchema>;
export type WorkEvent = z.infer<typeof WorkEventSchema>;

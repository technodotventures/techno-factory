import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

import type { WorkService } from "../application/work-service.js";
import { ClientGrantSchema } from "../domain/client-grant.js";
import { WorkEventSchema, WorkItemSchema } from "../domain/work-item.js";
import { WorkSubmissionSchema } from "../domain/work.js";

const SubmitWorkOutputSchema = z.object({
  created: z.boolean(),
  work: WorkItemSchema,
});
const WorkIdInputSchema = z.object({ workId: z.string().min(1) });
const GetWorkOutputSchema = z.object({ work: WorkItemSchema });
const ListWorkEventsOutputSchema = z.object({ events: z.array(WorkEventSchema) });

export interface FactoryMcpServerDependencies {
  workService: WorkService;
  grant: unknown;
}

export function createFactoryMcpServer(
  dependencies: FactoryMcpServerDependencies,
): McpServer {
  const grant = ClientGrantSchema.parse(dependencies.grant);
  const server = new McpServer({
    name: "techno-factory",
    version: "0.1.0",
  });

  server.registerTool(
    "submit_work",
    {
      title: "Submit factory work",
      description:
        "Submit an authenticated, project-scoped, idempotent work item to the Techno factory.",
      inputSchema: WorkSubmissionSchema,
      outputSchema: SubmitWorkOutputSchema,
      annotations: {
        readOnlyHint: false,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
    },
    async (submission) => {
      const result = dependencies.workService.submit(submission, grant);
      const structuredContent: Record<string, unknown> = {
        created: result.created,
        work: result.work,
      };
      return {
        content: [{ type: "text", text: JSON.stringify(result) }],
        structuredContent,
      };
    },
  );

  server.registerTool(
    "get_work",
    {
      title: "Get factory work",
      description: "Read one work item within the caller's project grant.",
      inputSchema: WorkIdInputSchema,
      outputSchema: GetWorkOutputSchema,
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
    },
    async ({ workId }) => {
      const work = dependencies.workService.get(workId, grant);
      const structuredContent: Record<string, unknown> = { work };
      return {
        content: [{ type: "text", text: JSON.stringify(structuredContent) }],
        structuredContent,
      };
    },
  );

  server.registerTool(
    "list_work_events",
    {
      title: "List factory work events",
      description: "Read the append-only audit events for one authorised work item.",
      inputSchema: WorkIdInputSchema,
      outputSchema: ListWorkEventsOutputSchema,
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
    },
    async ({ workId }) => {
      const events = dependencies.workService.listEvents(workId, grant);
      const structuredContent: Record<string, unknown> = { events };
      return {
        content: [{ type: "text", text: JSON.stringify(structuredContent) }],
        structuredContent,
      };
    },
  );

  return server;
}

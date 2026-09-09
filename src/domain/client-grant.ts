import { z } from "zod";

export const ClientPermissionSchema = z.enum([
  "work:submit",
  "work:read",
  "work:cancel",
]);

export const ClientGrantSchema = z.object({
  clientId: z.string().min(1),
  organizationId: z.string().min(1),
  workspaceId: z.string().min(1),
  projectIds: z.array(z.string().min(1)).min(1),
  permissions: z.array(ClientPermissionSchema).min(1),
});

export type ClientGrant = z.infer<typeof ClientGrantSchema>;
export type ClientPermission = z.infer<typeof ClientPermissionSchema>;

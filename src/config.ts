import { z } from "zod";

import { ClientGrantSchema } from "./domain/client-grant.js";
import type { HmacCredential } from "./infrastructure/hmac-auth.js";

const CredentialSchema = z.object({
  keyId: z.string().min(1),
  secret: z.string().min(32),
  grant: ClientGrantSchema,
});

const EnvironmentSchema = z.object({
  FACTORY_DATABASE_PATH: z.string().min(1).default("./data/factory.db"),
  FACTORY_HOST: z.string().min(1).default("127.0.0.1"),
  FACTORY_PORT: z.coerce.number().int().min(1).max(65_535).default(3000),
});

export interface FactoryConfig {
  databasePath: string;
  host: string;
  port: number;
  credentials: HmacCredential[];
}

export function loadConfig(environment: Record<string, string | undefined>): FactoryConfig {
  const rawCredentials = environment.FACTORY_CLIENTS_JSON;
  if (!rawCredentials) {
    throw new Error("FACTORY_CLIENTS_JSON is required");
  }

  let decoded: unknown;
  try {
    decoded = JSON.parse(rawCredentials);
  } catch {
    throw new Error("FACTORY_CLIENTS_JSON must be valid JSON");
  }

  const credentials = z.array(CredentialSchema).min(1).parse(decoded);
  const parsedEnvironment = EnvironmentSchema.parse(environment);
  return {
    databasePath: parsedEnvironment.FACTORY_DATABASE_PATH,
    host: parsedEnvironment.FACTORY_HOST,
    port: parsedEnvironment.FACTORY_PORT,
    credentials,
  };
}

import { describe, expect, it } from "vitest";

import { loadConfig } from "../src/config.js";

const clients = [
  {
    keyId: "coffee-local",
    secret: "0123456789abcdef0123456789abcdef",
    grant: {
      clientId: "coffee-local",
      organizationId: "techno-ventures",
      workspaceId: "protocols",
      projectIds: ["smartware", "expresso"],
      permissions: ["work:submit", "work:read"],
    },
  },
];

describe("loadConfig", () => {
  it("fails closed when client credentials are missing", () => {
    expect(() => loadConfig({})).toThrow("FACTORY_CLIENTS_JSON");
  });

  it("loads a valid local server configuration", () => {
    const config = loadConfig({
      FACTORY_CLIENTS_JSON: JSON.stringify(clients),
      FACTORY_DATABASE_PATH: "/tmp/factory.db",
      FACTORY_HOST: "127.0.0.1",
      FACTORY_PORT: "4040",
    });

    expect(config).toMatchObject({
      databasePath: "/tmp/factory.db",
      host: "127.0.0.1",
      port: 4040,
      credentials: [{ keyId: "coffee-local" }],
    });
  });
});

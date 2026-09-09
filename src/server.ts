import { mkdirSync } from "node:fs";
import { dirname } from "node:path";

import { WorkService } from "./application/work-service.js";
import { loadConfig } from "./config.js";
import { HmacAuthenticator } from "./infrastructure/hmac-auth.js";
import { SqliteReplayStore } from "./infrastructure/sqlite-replay-store.js";
import { SqliteWorkStore } from "./infrastructure/sqlite-work-store.js";
import { buildHttpApi } from "./transport/http-api.js";

const config = loadConfig(process.env);
mkdirSync(dirname(config.databasePath), { recursive: true });

const workStore = new SqliteWorkStore(config.databasePath);
const replayStore = new SqliteReplayStore(config.databasePath);
const authenticator = new HmacAuthenticator({
  credentials: config.credentials,
  replayStore,
});
const app = buildHttpApi({
  workService: new WorkService(workStore),
  authenticator,
});

let closing = false;
async function shutdown(signal: string): Promise<void> {
  if (closing) return;
  closing = true;
  console.log(JSON.stringify({ event: "factory.stopping", signal }));
  await app.close();
  replayStore.close();
  workStore.close();
}

process.once("SIGINT", () => void shutdown("SIGINT"));
process.once("SIGTERM", () => void shutdown("SIGTERM"));

try {
  await app.listen({ host: config.host, port: config.port });
  console.log(
    JSON.stringify({
      event: "factory.started",
      host: config.host,
      port: config.port,
    }),
  );
} catch (error) {
  replayStore.close();
  workStore.close();
  throw error;
}

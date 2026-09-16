import Fastify, { type FastifyInstance, type FastifyRequest } from "fastify";
import { ZodError } from "zod";

import type { WorkService } from "../application/work-service.js";
import {
  AuthenticationError,
  AuthorizationError,
  IdempotencyConflictError,
  WorkNotFoundError,
} from "../domain/errors.js";
import type { HmacAuthenticator } from "../infrastructure/hmac-auth.js";

declare module "fastify" {
  interface FastifyRequest {
    rawBody: string;
  }
}

export interface HttpApiDependencies {
  workService: WorkService;
  authenticator: HmacAuthenticator;
}

function authenticate(
  request: FastifyRequest,
  authenticator: HmacAuthenticator,
) {
  return authenticator.authenticate({
    method: request.method,
    path: request.raw.url ?? request.url,
    body: request.rawBody ?? "",
    headers: request.headers,
  });
}

export function buildHttpApi(dependencies: HttpApiDependencies): FastifyInstance {
  const app = Fastify({ logger: false });

  app.removeContentTypeParser("application/json");
  app.addContentTypeParser(
    "application/json",
    { parseAs: "string" },
    (request, body, done) => {
      const rawBody = typeof body === "string" ? body : body.toString("utf8");
      request.rawBody = rawBody;
      try {
        done(null, JSON.parse(rawBody));
      } catch (error) {
        done(error as Error, undefined);
      }
    },
  );

  app.get("/health", async () => ({ status: "ok" }));

  app.post("/v1/work", async (request, reply) => {
    const grant = authenticate(request, dependencies.authenticator);
    const result = dependencies.workService.submit(request.body, grant);
    return reply.code(result.created ? 201 : 200).send(result);
  });

  app.get<{ Params: { workId: string } }>("/v1/work/:workId", async (request) => {
    const grant = authenticate(request, dependencies.authenticator);
    return dependencies.workService.get(request.params.workId, grant);
  });

  app.get<{ Params: { workId: string } }>(
    "/v1/work/:workId/events",
    async (request) => {
      const grant = authenticate(request, dependencies.authenticator);
      return {
        events: dependencies.workService.listEvents(request.params.workId, grant),
      };
    },
  );

  app.setErrorHandler((error, _request, reply) => {
    if (error instanceof AuthenticationError) {
      return reply.code(401).send({ error: "authentication_failed" });
    }
    if (error instanceof AuthorizationError) {
      return reply.code(403).send({ error: "forbidden" });
    }
    if (error instanceof WorkNotFoundError) {
      return reply.code(404).send({ error: "not_found" });
    }
    if (error instanceof IdempotencyConflictError) {
      return reply.code(409).send({ error: "idempotency_conflict" });
    }
    if (error instanceof ZodError) {
      return reply.code(400).send({ error: "invalid_request", issues: error.issues });
    }
    return reply.code(500).send({ error: "internal_error" });
  });

  return app;
}

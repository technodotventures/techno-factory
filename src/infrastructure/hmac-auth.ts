import { createHash, createHmac, timingSafeEqual } from "node:crypto";

import { ClientGrantSchema, type ClientGrant } from "../domain/client-grant.js";
import { AuthenticationError } from "../domain/errors.js";

export interface HmacCredential {
  keyId: string;
  secret: string;
  grant: ClientGrant;
}

export interface ReplayStore {
  consume(keyId: string, nonce: string, expiresAtMs: number, nowMs: number): boolean;
}

export class MemoryReplayStore implements ReplayStore {
  private readonly entries = new Map<string, number>();

  consume(keyId: string, nonce: string, expiresAtMs: number, nowMs: number): boolean {
    for (const [key, expiry] of this.entries) {
      if (expiry <= nowMs) this.entries.delete(key);
    }
    const key = `${keyId}:${nonce}`;
    if (this.entries.has(key)) return false;
    this.entries.set(key, expiresAtMs);
    return true;
  }
}

export interface SignableRequest {
  secret: string;
  method: string;
  path: string;
  timestamp: string;
  nonce: string;
  body: string;
}

function canonicalRequest(input: Omit<SignableRequest, "secret">): string {
  const bodyHash = createHash("sha256").update(input.body).digest("hex");
  return [
    input.method.toUpperCase(),
    input.path,
    input.timestamp,
    input.nonce,
    bodyHash,
  ].join("\n");
}

export function signRequest(input: SignableRequest): string {
  return createHmac("sha256", input.secret)
    .update(canonicalRequest(input))
    .digest("hex");
}

export interface AuthenticationRequest {
  method: string;
  path: string;
  body: string;
  headers: Record<string, string | string[] | undefined>;
}

export interface HmacAuthenticatorOptions {
  credentials: HmacCredential[];
  replayStore: ReplayStore;
  now?: () => number;
  maxClockSkewSeconds?: number;
}

function requiredHeader(
  headers: AuthenticationRequest["headers"],
  name: string,
): string {
  const value = headers[name];
  if (typeof value !== "string" || value.length === 0) {
    throw new AuthenticationError(`Missing ${name}`);
  }
  return value;
}

export class HmacAuthenticator {
  private readonly credentials: Map<string, HmacCredential>;
  private readonly now: () => number;
  private readonly maxClockSkewSeconds: number;

  constructor(private readonly options: HmacAuthenticatorOptions) {
    this.credentials = new Map(
      options.credentials.map((credential) => [credential.keyId, credential]),
    );
    this.now = options.now ?? Date.now;
    this.maxClockSkewSeconds = options.maxClockSkewSeconds ?? 300;
  }

  authenticate(request: AuthenticationRequest): ClientGrant {
    const keyId = requiredHeader(request.headers, "x-factory-key-id");
    const timestamp = requiredHeader(request.headers, "x-factory-timestamp");
    const nonce = requiredHeader(request.headers, "x-factory-nonce");
    const suppliedSignature = requiredHeader(request.headers, "x-factory-signature");
    const credential = this.credentials.get(keyId);
    if (!credential) throw new AuthenticationError("Unknown client key");

    const timestampSeconds = Number(timestamp);
    const nowMs = this.now();
    if (
      !Number.isSafeInteger(timestampSeconds) ||
      Math.abs(Math.floor(nowMs / 1000) - timestampSeconds) > this.maxClockSkewSeconds
    ) {
      throw new AuthenticationError("Request timestamp is outside the allowed window");
    }

    const expectedSignature = signRequest({
      secret: credential.secret,
      method: request.method,
      path: request.path,
      timestamp,
      nonce,
      body: request.body,
    });
    const supplied = Buffer.from(suppliedSignature, "hex");
    const expected = Buffer.from(expectedSignature, "hex");
    if (supplied.length !== expected.length || !timingSafeEqual(supplied, expected)) {
      throw new AuthenticationError("Invalid request signature");
    }

    const expiresAtMs = (timestampSeconds + this.maxClockSkewSeconds) * 1000;
    if (!this.options.replayStore.consume(keyId, nonce, expiresAtMs, nowMs)) {
      throw new AuthenticationError("Request nonce has already been used");
    }

    return ClientGrantSchema.parse(credential.grant);
  }
}

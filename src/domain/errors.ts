export class AuthorizationError extends Error {
  override readonly name = "AuthorizationError";
}

export class AuthenticationError extends Error {
  override readonly name = "AuthenticationError";
}

export class IdempotencyConflictError extends Error {
  override readonly name = "IdempotencyConflictError";
}

export class WorkNotFoundError extends Error {
  override readonly name = "WorkNotFoundError";
}

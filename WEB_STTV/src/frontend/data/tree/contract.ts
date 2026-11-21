export class SttvTreeError extends Error {
  constructor(readonly code: string, reason: string, readonly details: Record<string, unknown>) {
    super(reason);
  }
}

export function sttvTreeError(code: string, reason: string, details: Record<string, unknown> = {}): never {
  throw new SttvTreeError(code, reason, details);
}

import { SttvPreparationError, sttvDiagnostic, type SttvDiagnosticCode } from '../../workers/diagnostics';

export function sttvTreeError(code: SttvDiagnosticCode, reason: string, details: Record<string, unknown> = {}): never {
  throw new SttvPreparationError(sttvDiagnostic(code, 'preparing', { reason, ...details }));
}
export function sttvRecord(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}

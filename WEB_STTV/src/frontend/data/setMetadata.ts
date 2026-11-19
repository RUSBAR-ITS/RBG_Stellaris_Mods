import { SttvPreparationError, sttvDiagnostic } from '../workers/diagnostics';

export function sttvSetError(reason: string, details: Record<string, unknown> = {}): never {
  throw new SttvPreparationError(sttvDiagnostic('invalid_database_set', 'preparing', { reason, ...details }));
}

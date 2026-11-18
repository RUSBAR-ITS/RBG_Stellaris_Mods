import config from '../../../config/frontend/diagnostics.json';
import type { SttvNodeRef } from '../data/model';

export type SttvPhase = 'reading' | 'parsing' | 'preparing';
export type SttvDiagnosticCode = keyof typeof config.messages;
export interface SttvDiagnostic {
  severity: 'warning' | 'error';
  code: SttvDiagnosticCode;
  phase: SttvPhase | null;
  params: Record<string, never>;
  details: Record<string, unknown>;
}
export function sttvDiagnostic(code: SttvDiagnosticCode, phase: SttvPhase | null,
  details: Record<string, unknown> = {}): SttvDiagnostic {
  return { severity: code === 'missing_localization' ? 'warning' : 'error', code,
    phase, params: {}, details };
}
export class SttvPreparationError extends Error {
  constructor(public diagnostic: SttvDiagnostic) {
    super(diagnostic.code);
  }
}
export function sttvInvalid(path: string | SttvNodeRef, reason: string) {
  return new SttvPreparationError(sttvDiagnostic('invalid_database', 'preparing',
    { ...(typeof path === 'string' ? { path } : { sourceRef: path }), reason }));
}
export function sttvExceptionDetails(error: unknown): Record<string, unknown> {
  return error instanceof Error ? { name: error.name, message: error.message } : {};
}

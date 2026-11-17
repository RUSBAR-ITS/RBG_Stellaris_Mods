import type { SttvCatalog } from '../data/model';
import type { SttvDiagnostic, SttvPhase } from './diagnostics';

export interface SttvOpenCommand { type: 'open_database'; operationId: number; file: File }
export type SttvWorkerMessage =
  | { type: 'progress'; operationId: number; phase: SttvPhase }
  | { type: 'ready'; operationId: number; data: SttvCatalog }
  | { type: 'error'; operationId: number; error: SttvDiagnostic; diagnostics: SttvDiagnostic[] };

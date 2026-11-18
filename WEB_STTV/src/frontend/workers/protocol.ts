import type { SttvCatalog, SttvDatabaseKind } from '../data/model';
import type { SttvDiagnostic, SttvPhase } from './diagnostics';

export interface SttvOpenCommand { type: 'open_database_set'; operationId: number; files: File[] }
export interface SttvFileProgress {
  fileIndex: number;
  total: number;
  kind: SttvDatabaseKind | null;
  setId: string | null;
}
export type SttvWorkerMessage =
  | { type: 'progress'; operationId: number; phase: SttvPhase; file: SttvFileProgress }
  | { type: 'ready'; operationId: number; data: SttvCatalog }
  | { type: 'error'; operationId: number; error: SttvDiagnostic; diagnostics: SttvDiagnostic[] };

import type { SttvCatalog, SttvDatabaseKind, SttvNodeRef, SttvObjectRef } from '../data/model';
import type { SttvDiagnostic, SttvPhase } from './diagnostics';
import type { SttvCoverage } from '../storage/model';

export interface SttvOpenCommand { type: 'open_database_set'; operationId: number; files: File[] }
export type SttvCommand = SttvOpenCommand
  | { type: 'apply_dlc'; operationId: number; requestId: number; snapshotRevision: string; enabled: string[] }
  | { type: 'cancel_dlc'; operationId: number; requestId: number; snapshotRevision: string }
  | { type: 'load_datasets'; operationId: number; requestId: number; snapshotRevision: string; kinds: SttvDatabaseKind[] }
  | { type: 'resolve_nodes'; operationId: number; requestId: number; snapshotRevision: string; refs: SttvNodeRef[] }
  | { type: 'resolve_objects'; operationId: number; requestId: number; snapshotRevision: string; objects: SttvObjectRef[] };
export interface SttvFileProgress {
  fileIndex: number;
  total: number;
  kind: SttvDatabaseKind | null;
  setId: string | null;
  documentId?: string;
}
export type SttvWorkerMessage =
  | { type: 'api_operation'; operationId: number; jobId: string | null; token: string }
  | { type: 'progress'; operationId: number; phase: SttvPhase; file: SttvFileProgress }
  | { type: 'ready'; operationId: number; data: SttvCatalog }
  | { type: 'loaded'; operationId: number; requestId: number; snapshotRevision: string; data: SttvCatalog; refs: SttvNodeRef[] }
  | { type: 'load_error'; operationId: number; requestId: number; snapshotRevision: string; error: SttvDiagnostic; coverage?: SttvCoverage }
  | { type: 'error'; operationId: number; error: SttvDiagnostic; diagnostics: SttvDiagnostic[] };

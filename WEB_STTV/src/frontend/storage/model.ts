import type { SttvDatabaseKind } from '../data/model';

export interface SttvDocumentDescriptor {
  document_id: string;
  source: { root: string; file: string };
  path: string;
  byte_size: number;
  file_hash: string;
  source_hash: string;
  item_count: number;
}
export interface SttvObjectEntry {
  id: string | null;
  type: string;
  document_id: string;
  pointer: string;
}
export interface SttvManifest {
  presentation?: import('./assets').SttvPresentation;
  technology_tree?: unknown;
  format: 'sttv.database_manifest';
  format_version: 2;
  acquisition: {
    format_version: 1;
    revision: string;
    documents: { path: string; file_hash: string; byte_size: number }[];
  };
  set_id: string;
  snapshot_revision: string;
  registry_revision: string;
  datasets: Record<SttvDatabaseKind, {
    source_revision: string;
    documents: SttvDocumentDescriptor[];
    objects: SttvObjectEntry[];
  }>;
}
export interface SttvCoverage {
  declaredDocuments: number;
  verifiedDocuments: number;
  notCheckedDocuments: number;
  bytesRead: number;
  seconds: number;
  documents: { database: SttvDatabaseKind; document_id: string; path: string;
    state: 'not_loaded' | 'loading' | 'loaded' | 'failed';
    status: 'verified' | 'not_checked' }[];
}

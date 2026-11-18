import config from '../../../config/frontend/adapter.json';
import { sttvDatabaseKinds } from './registry';
import type { SttvDatabaseKind, SttvDatasetInfo } from './model';
import type { SttvDatabase } from './syntax';
import { SttvPreparationError, sttvDiagnostic } from '../workers/diagnostics';

export function sttvSetError(reason: string, details: Record<string, unknown> = {}): never {
  throw new SttvPreparationError(sttvDiagnostic('invalid_database_set', 'preparing', { reason, ...details }));
}
export function sttvCheckMember(input: unknown, fileIndex: number) {
  const db = input as SttvDatabase;
  if (db?.format !== config.format || db?.format_version !== config.formatVersion) {
    sttvSetError('Unsupported database format.', { fileIndex, expectedVersion: config.formatVersion,
      receivedVersion: db?.format_version ?? null });
  }
  if (!db.dataset || !sttvDatabaseKinds.includes(db.dataset.kind as SttvDatabaseKind)
    || typeof db.dataset.set_id !== 'string' || !/^[a-f0-9]{64}$/.test(db.dataset.set_id)) {
    sttvSetError('Missing or invalid dataset metadata.', { fileIndex, dataset: db.dataset ?? null });
  }
  if (!Array.isArray(db.documents)) sttvSetError('Source documents are missing.', { fileIndex });
  return { kind: db.dataset.kind as SttvDatabaseKind, setId: db.dataset.set_id };
}
export class SttvSetMetadata {
  readonly datasets: SttvDatasetInfo[] = [];
  private seen = new Set<SttvDatabaseKind>();
  setId = '';
  constructor(readonly files: { name: string; size: number }[]) {
    if (files.length !== sttvDatabaseKinds.length) sttvSetError('Incorrect number of database files.', {
      count: files.length, expected: sttvDatabaseKinds.length });
  }
  add(input: unknown, fileIndex: number) {
    const member = sttvCheckMember(input, fileIndex);
    const details = { fileIndex, kind: member.kind, missing: sttvDatabaseKinds.filter(kind => !this.seen.has(kind)) };
    if (this.seen.has(member.kind)) sttvSetError('Duplicate dataset role.', { ...details, duplicate: member.kind });
    if (this.setId && this.setId !== member.setId) sttvSetError('Files belong to different database sets.', {
      ...details, expectedSetId: this.setId, receivedSetId: member.setId });
    this.setId = member.setId;
    this.seen.add(member.kind);
    this.datasets.push({ ...this.files[fileIndex], kind: member.kind, fileIndex,
      documentCount: (input as SttvDatabase).documents.length });
    return member;
  }
  finish() {
    const missing = sttvDatabaseKinds.filter(kind => !this.seen.has(kind));
    if (missing.length) sttvSetError('Missing database roles.', { missing });
  }
}

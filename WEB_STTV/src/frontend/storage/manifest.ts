import storage from '../../../config/storage.json';
import registry from '../../../config/datasets.json';
import { sha256 } from '@noble/hashes/sha2.js';
import { bytesToHex } from '@noble/hashes/utils.js';
import { sttvDatabaseKinds, sttvDatasets } from '../data/registry';
import type { SttvDatabaseKind } from '../data/model';
import { sttvSetError } from '../data/setMetadata';
import { sttvReadJson } from '../data/jsonStream';
import type { SttvManifest } from './model';
import { sttvCheckPresentation } from './assets';

export function sttvRelative(path: string) {
  if (typeof path !== 'string' || !path || /[:\\]/.test(path)
    || path.split('/').some(part => ['', '.', '..'].includes(part))) sttvSetError('Unsafe relative path.', { path });
  return path;
}
function canonical(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value && typeof value === 'object') return `{${Object.keys(value).sort().map(key =>
    `${JSON.stringify(key)}:${canonical((value as Record<string, unknown>)[key])}`).join(',')}}`;
  return JSON.stringify(value);
}
const hashPattern = /^[a-f0-9]{64}$/;
function hash(value: unknown) { return typeof value === 'string' && hashPattern.test(value); }

export function sttvCheckManifest(input: unknown): SttvManifest {
  const manifest = input as SttvManifest;
  if (manifest?.format !== 'sttv.database_manifest' || manifest.format_version !== 1
    || !hash(manifest.set_id) || !hash(manifest.snapshot_revision) || !hash(manifest.registry_revision)) {
    sttvSetError('Unsupported or invalid manifest.');
  }
  const expectedRegistry = bytesToHex(sha256(new TextEncoder().encode(canonical(registry))));
  if (manifest.registry_revision !== expectedRegistry) sttvSetError('Object registry revision differs.');
  if (!manifest.datasets || Object.keys(manifest.datasets).sort().join() !== [...sttvDatabaseKinds].sort().join()) {
    sttvSetError('Manifest must declare every dataset exactly once.');
  }
  const paths = new Set<string>(), documentIds = new Set<string>();
  for (const kind of sttvDatabaseKinds) {
    const dataset = manifest.datasets[kind], spec = sttvDatasets[kind];
    if (!hash(dataset.source_revision) || !Array.isArray(dataset.documents) || !Array.isArray(dataset.objects)) {
      sttvSetError('Invalid dataset inventory.', { kind });
    }
    const documents = new Map<string, number>(), identities = new Set<string>(), addresses = new Set<string>();
    for (const row of dataset.documents) {
      const path = sttvRelative(row.path).toLowerCase();
      if (!hash(row.document_id) || !hash(row.file_hash) || !hash(row.source_hash)
        || !Number.isSafeInteger(row.byte_size) || row.byte_size < 0
        || !Number.isSafeInteger(row.item_count) || row.item_count < 0
        || typeof row.source?.root !== 'string' || typeof row.source?.file !== 'string') {
        sttvSetError('Invalid document descriptor.', { kind, document: row });
      }
      sttvRelative(row.source.file);
      if (paths.has(path) || documentIds.has(row.document_id)) sttvSetError('Conflicting document paths or identities.', { kind, path });
      paths.add(path); documentIds.add(row.document_id); documents.set(row.document_id, row.item_count);
    }
    for (const row of dataset.objects) {
      const count = documents.get(row.document_id), address = row.document_id + row.pointer;
      if (typeof row.type !== 'string' || !/^\/items\/(0|[1-9]\d*)$/.test(row.pointer)
        || count === undefined || Number(row.pointer.slice(7)) >= count || addresses.has(address)
        || (spec.identity === 'anonymous' ? row.id !== null : typeof row.id !== 'string' || !row.id)) {
        sttvSetError('Invalid object index entry.', { kind, entry: row });
      }
      if (row.id !== null && identities.has(row.id) && spec.identity !== 'fragments') {
        sttvSetError('Conflicting object ID.', { kind, id: row.id });
      }
      addresses.add(address); if (row.id !== null) identities.add(row.id);
    }
  }
  if (manifest.presentation) sttvCheckPresentation(manifest.presentation, sttvRelative, paths);
  return manifest;
}

export async function sttvOpenDirectory(files: File[]) {
  const map = new Map<string, File>(), folded = new Set<string>();
  let root: string | undefined;
  for (const file of files) {
    const relative = sttvRelative(file.webkitRelativePath), slash = relative.indexOf('/');
    if (slash < 1) sttvSetError('Select a directory containing the manifest.');
    const first = relative.slice(0, slash), path = relative.slice(slash + 1);
    if (root !== undefined && root !== first) sttvSetError('Files have different directory roots.');
    root = first;
    if (folded.has(path.toLowerCase())) sttvSetError('Conflicting selected paths.', { path });
    folded.add(path.toLowerCase()); map.set(path, file);
  }
  const source = map.get(storage.manifest);
  if (!source) sttvSetError('Root manifest is missing.', { manifest: storage.manifest });
  const parsed = await sttvReadJson(source, undefined, true);
  const manifest = sttvCheckManifest(parsed.metadata);
  for (const [kind, dataset] of Object.entries(manifest.datasets)) {
    for (const row of dataset.documents) if (!map.has(row.path)) {
      sttvSetError('Declared document is missing.', { kind, document_id: row.document_id, path: row.path });
    }
  }
  return { manifest, files: map, manifestBytes: parsed.bytes };
}

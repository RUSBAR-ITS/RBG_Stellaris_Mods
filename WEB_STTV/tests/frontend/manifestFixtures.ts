import { createHash } from 'node:crypto';
import registry from '../../config/datasets.json' with { type: 'json' };
import type { SttvDatabase } from '../../src/frontend/data/syntax';
import type { SttvManifest } from '../../src/frontend/storage/model';
import { sttvDatabaseKinds, sttvDatasets } from '../../src/frontend/data/registry';
import { sttvSetError } from '../../src/frontend/data/setMetadata';

export const sttvHash = (text: string) => createHash('sha256').update(text).digest('hex');
function canonical(v: unknown): string {
  if (Array.isArray(v)) return `[${v.map(canonical).join(',')}]`;
  if (v && typeof v === 'object') return `{${Object.keys(v).sort().map(k =>
    `${JSON.stringify(k)}:${canonical((v as Record<string, unknown>)[k])}`).join(',')}}`;
  return JSON.stringify(v);
}
export function sttvBundle(inputs: SttvDatabase[]) {
  const manifest: SttvManifest = { format: 'sttv.database_manifest', format_version: 1,
    set_id: 'a'.repeat(64), snapshot_revision: 'b'.repeat(64), registry_revision: sttvHash(canonical(registry)),
    datasets: Object.create(null) };
  const entries: { path: string; content: string }[] = [];
  for (const kind of sttvDatabaseKinds) manifest.datasets[kind] = { documents: [], objects: [], source_revision: 'c'.repeat(64) };
  for (const db of inputs) {
    if (!sttvDatabaseKinds.includes(db.database)) sttvSetError('Unknown dataset.');
    const dataset = manifest.datasets[db.database], spec = sttvDatasets[db.database];
    const content = JSON.stringify(db, null, 2) + '\n', file_hash = sttvHash(content);
    const path = `documents/${db.database}/${db.document_id}/${file_hash}.json`;
    entries.push({ path, content });
    dataset.documents.push({ document_id: db.document_id, source: db.source, path, file_hash,
      source_hash: file_hash, byte_size: Buffer.byteLength(content), item_count: db.items.length });
    db.items.forEach((node, i) => {
      if (node.kind !== 'assignment' || node.value?.kind !== 'block' || !node.key?.text
        || spec.rootTypes.length && !(spec.rootTypes as string[]).includes(node.key.text)) return;
      const id = spec.identity === 'anonymous' ? null : spec.idField
        ? node.value.items?.find(n => n.key?.text === spec.idField)?.value?.text ?? '' : node.key.text;
      dataset.objects.push({ id, type: node.key.text, document_id: db.document_id, pointer: `/items/${i}` });
    });
  }
  entries.push({ path: 'manifest.json', content: JSON.stringify(manifest, null, 2) + '\n' });
  return { manifest, entries };
}
export function sttvFiles(inputs: SttvDatabase[]) {
  return sttvBundle(inputs).entries.map(entry => {
    const file = new File([entry.content], entry.path.split('/').at(-1)!);
    Object.defineProperty(file, 'webkitRelativePath', { value: 'example/' + entry.path });
    return file;
  });
}

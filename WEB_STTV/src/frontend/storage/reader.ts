import type { SttvDatabaseKind, SttvNodeRef } from '../data/model';
import type { SttvDatabase, SttvNode } from '../data/syntax';
import { sttvDatasets } from '../data/registry';
import { sttvReadJson } from '../data/jsonStream';
import { sttvSetError } from '../data/setMetadata';
import type { SttvManifest, SttvObjectEntry, SttvCoverage } from './model';

export class SttvDocumentReader {
  private verified = new Set<string>();
  private states = new Map<string, 'loading' | 'loaded' | 'failed'>();
  bytes = 0;
  seconds = 0;
  constructor(readonly manifest: SttvManifest, private files: Map<string, File>) {}

  resolve(kind: SttvDatabaseKind, id: string): SttvNodeRef[] {
    return this.manifest.datasets[kind].objects.filter(row => row.id === id)
      .map(({ document_id, pointer }) => ({ database: kind, document_id, pointer }));
  }
  async read(kind: SttvDatabaseKind, identifier: string,
    consume: (document: SttvDatabase, itemOffset: number) => void) {
    this.states.set(identifier, 'loading');
    try {
      await this.readDocument(kind, identifier, consume);
      this.states.set(identifier, 'loaded');
    } catch (error) { this.states.set(identifier, 'failed'); throw error; }
  }
  private async readDocument(kind: SttvDatabaseKind, identifier: string,
    consume: (document: SttvDatabase, itemOffset: number) => void) {
    const dataset = this.manifest.datasets[kind];
    const descriptor = dataset.documents.find(row => row.document_id === identifier);
    if (!descriptor) sttvSetError('Unknown document.', { kind, document_id: identifier });
    const file = this.files.get(descriptor.path)!;
    const details = { database: kind, document_id: identifier, path: descriptor.path,
      snapshotRevision: this.manifest.snapshot_revision, sourceFile: descriptor.source.file };
    if (file.size !== descriptor.byte_size) sttvSetError('Document size mismatch.', details);
    const start = performance.now(), objects: SttvObjectEntry[] = [];
    const header = { format: 'sttv.parse_document', format_version: 1, database: kind,
      document_id: identifier, source: descriptor.source };
    const spec = sttvDatasets[kind];
    const parsed = await sttvReadJson(file, (node: SttvNode, index) => {
      const pointer = `/items/${index}`;
      if (node?.kind === 'assignment' && node.value?.kind === 'block'
        && (!spec.rootTypes.length || (spec.rootTypes as string[]).includes(node.key?.text ?? ''))) {
        const values = spec.idField ? node.value.items?.filter(n => n.kind === 'assignment' && n.key?.text === spec.idField) : [];
        const id = spec.identity === 'anonymous' ? null : spec.idField ? values?.[0]?.value?.text : node.key?.text;
        if (spec.idField && values?.length !== 1 || id === undefined || !node.key?.text) sttvSetError('Invalid object identity.', { ...details, pointer });
        objects.push({ id: id!, type: node.key!.text!, document_id: identifier, pointer });
      }
      consume({ ...header, items: [node] }, index);
    });
    this.bytes += parsed.bytes; this.seconds += (performance.now() - start) / 1000;
    if (parsed.hash !== descriptor.file_hash) sttvSetError('Document hash mismatch.', {
      ...details, expectedHash: descriptor.file_hash, actualHash: parsed.hash });
    const actual = parsed.metadata;
    if (actual.format !== header.format || actual.format_version !== 1 || actual.database !== kind
      || actual.document_id !== identifier || actual.source?.root !== header.source.root
      || actual.source?.file !== header.source.file || parsed.itemCount !== descriptor.item_count) {
      sttvSetError('Document envelope differs from the manifest.', details);
    }
    const expected = dataset.objects.filter(row => row.document_id === identifier);
    if (objects.length !== expected.length || objects.some((row, i) =>
      row.id !== expected[i].id || row.type !== expected[i].type || row.pointer !== expected[i].pointer)) {
      sttvSetError('Object index differs from document contents.', details);
    }
    this.verified.add(identifier);
  }
  coverage(): SttvCoverage {
    const documents = Object.entries(this.manifest.datasets).flatMap(([kind, dataset]) => dataset.documents.map(row => ({
      database: kind as SttvDatabaseKind, document_id: row.document_id, path: row.path,
      state: this.states.get(row.document_id) ?? 'not_loaded' as const,
      status: this.verified.has(row.document_id) ? 'verified' as const : 'not_checked' as const,
    })));
    return { declaredDocuments: documents.length, verifiedDocuments: this.verified.size,
      notCheckedDocuments: documents.length - this.verified.size, documents, bytesRead: this.bytes, seconds: this.seconds };
  }
}

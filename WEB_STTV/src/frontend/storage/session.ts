import opening from '../../../config/frontend/opening.json';
import type { SttvDatabaseKind, SttvObjectRef, SttvNodeRef } from '../data/model';
import type { SttvTargetRegistry } from '../data/textTargets';
import { sttvDatabaseKinds } from '../data/registry';
import { SttvSetAdapter } from '../data/setAdapter';
import { sttvSetError } from '../data/setMetadata';
import { sttvOpenDirectory } from './manifest';
import { SttvDocumentReader } from './reader';
import { sttvLoadAssets, type SttvCachedImage } from './assets';
import { SttvPreparationError, sttvDiagnostic } from '../workers/diagnostics';
import { sttvCheckManifest } from './manifest';
import { sttvSnapshotFiles, type SttvRemoteBytes } from './bytes';

export class SttvStorageSession {
  private tail: Promise<unknown> = Promise.resolve();
  private images = new Map<string, SttvCachedImage>();
  private constructor(readonly reader: SttvDocumentReader, private adapter: SttvSetAdapter) {}
  get combinationId() { return this.adapter.treeCombination.id; }
  static async open(files: File[], rules: SttvTargetRegistry, combinationId?: string) {
    const { manifest, files: mapped } = await sttvOpenDirectory(files);
    if (!manifest.presentation) throw new SttvPreparationError(sttvDiagnostic('assets_not_prepared', 'preparing'));
    return new SttvStorageSession(new SttvDocumentReader(manifest, mapped), new SttvSetAdapter(manifest, rules, [], combinationId));
  }
  static fromSnapshot(input: unknown, files: Map<string, File>, rules: SttvTargetRegistry,
    combinationId: string, remote?: SttvRemoteBytes) {
    const manifest = sttvCheckManifest(input);
    return new SttvStorageSession(new SttvDocumentReader(manifest, sttvSnapshotFiles(manifest, files), remote),
      new SttvSetAdapter(manifest, rules, [], combinationId));
  }
  async refresh(input: unknown, combinationId: string, remote: SttvRemoteBytes) {
    await this.tail;
    const manifest = sttvCheckManifest(input), adapter = this.adapter.rebase(manifest, combinationId);
    const reader = new SttvDocumentReader(manifest, sttvSnapshotFiles(manifest, this.reader.files), remote);
    reader.inherit(this.reader);
    const next = new SttvStorageSession(reader, adapter);
    next.images = new Map(this.images);
    const data = await next.initial();
    return { session: next, data };
  }
  initial(progress?: (kind: SttvDatabaseKind, identifier: string) => void) {
    return this.load(opening.initial_datasets as SttvDatabaseKind[], progress);
  }
  load(kinds: SttvDatabaseKind[], progress?: (kind: SttvDatabaseKind, identifier: string) => void) {
    if (kinds.some(kind => !sttvDatabaseKinds.includes(kind))) sttvSetError('Unknown dataset request.');
    const refs = [...new Set(kinds)].flatMap(kind => this.reader.manifest.datasets[kind].documents.map(row =>
      ({ database: kind, document_id: row.document_id, pointer: '' })));
    return this.enqueue(refs, kinds, progress);
  }
  resolve(objects: SttvObjectRef[]) {
    const refs = objects.flatMap(object => {
      if (!sttvDatabaseKinds.includes(object.database)) sttvSetError('Unknown object dataset.');
      const found = this.reader.resolve(object.database, object.id);
      if (!found.length) sttvSetError('Object is not in the manifest.', { object });
      return found;
    });
    return this.enqueue(refs, []).then(data => ({ data, refs }));
  }
  resolveNodes(refs: SttvNodeRef[]) {
    for (const ref of refs) {
      const dataset = this.reader.manifest.datasets[ref.database];
      if (!dataset?.objects.some(row => row.document_id === ref.document_id && row.pointer === ref.pointer)) {
        sttvSetError('Node reference is not in the manifest.', { sourceRef: ref });
      }
    }
    return this.enqueue(refs, []).then(data => ({ data, refs }));
  }
  private enqueue(refs: SttvNodeRef[], completeKinds: SttvDatabaseKind[],
    progress?: (kind: SttvDatabaseKind, identifier: string) => void) {
    const operation = this.tail.then(async () => {
      const trial = this.adapter.fork();
      for (const kind of completeKinds) trial.datasets.find(row => row.kind === kind)!.state = 'loading';
      for (const ref of refs) {
        if (trial.loadedDocuments.has(ref.document_id)) continue;
        progress?.(ref.database, ref.document_id);
        await this.reader.read(ref.database, ref.document_id, (doc, offset) => trial.document(doc, offset));
        trial.completed(ref.database, ref.document_id);
      }
      for (const kind of completeKinds) trial.datasets.find(row => row.kind === kind)!.state = 'loaded';
      const catalog = trial.finish(this.reader.coverage());
      await sttvLoadAssets(catalog, this.reader.manifest.presentation!, this.reader.files, this.images, this.reader.remote);
      this.adapter = trial;
      return catalog;
    });
    this.tail = operation.catch(() => undefined);
    return operation;
  }
}

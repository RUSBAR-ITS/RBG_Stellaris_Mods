import opening from '../../../config/frontend/opening.json';
import type { SttvDatabaseKind, SttvObjectRef, SttvNodeRef } from '../data/model';
import type { SttvTargetRegistry } from '../data/textTargets';
import { sttvDatabaseKinds } from '../data/registry';
import { SttvSetAdapter } from '../data/setAdapter';
import { sttvSetError } from '../data/setMetadata';
import { sttvOpenDirectory } from './manifest';
import { SttvDocumentReader } from './reader';

export class SttvStorageSession {
  private tail: Promise<unknown> = Promise.resolve();
  private constructor(readonly reader: SttvDocumentReader, private adapter: SttvSetAdapter) {}
  static async open(files: File[], rules: SttvTargetRegistry) {
    const { manifest, files: mapped } = await sttvOpenDirectory(files);
    return new SttvStorageSession(new SttvDocumentReader(manifest, mapped), new SttvSetAdapter(manifest, rules));
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
      const rootPointer = ref.pointer.match(/^\/items\/\d+(?:\/|$)/)?.[0].replace(/\/$/, '');
      if (!dataset?.objects.some(row => row.document_id === ref.document_id && row.pointer === rootPointer)) {
        sttvSetError('Node reference is not in the manifest.', { sourceRef: ref });
      }
      if (ref.pointer !== rootPointer) sttvSetError('Direct loading requires a root object reference.', { sourceRef: ref });
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
      this.adapter = trial;
      return catalog;
    });
    this.tail = operation.catch(() => undefined);
    return operation;
  }
}

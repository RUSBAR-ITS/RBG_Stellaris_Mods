import type { SttvCatalog, SttvDatabaseKind, SttvNodeRef, SttvObjectRef } from '../data/model';
import type { SttvDiagnostic, SttvPhase } from './diagnostics';
import { sttvDiagnostic, sttvExceptionDetails } from './diagnostics';
import type { SttvWorkerMessage, SttvFileProgress } from './protocol';
import service from '../../../config/service.json';

export type SttvOpeningStatus = 'idle' | 'loading' | 'ready' | 'empty' | 'error';
export interface SttvOpening {
  status: SttvOpeningStatus;
  operationId: number;
  files: File[];
  progress: SttvFileProgress | null;
  members: SttvFileProgress[];
  phase: SttvPhase | null;
  data: SttvCatalog | null;
  error: SttvDiagnostic | null;
  diagnostics: SttvDiagnostic[];
}
export type SttvWorkerPort = Pick<Worker, 'postMessage' | 'terminate' | 'onmessage' | 'onerror' | 'onmessageerror'>;
export const sttvIdle: SttvOpening = { status: 'idle', operationId: 0, files: [], progress: null, members: [],
  phase: null, data: null, error: null, diagnostics: [] };

export class SttvOpeningController {
  state: SttvOpening = sttvIdle;
  private serial = 0;
  private worker: SttvWorkerPort | null = null;
  private requestSerial = 0;
  private activeApi: { jobId: string; token: string } | null = null;
  private pending = new Map<number, { revision: string; kinds: SttvDatabaseKind[];
    resolve: (refs: SttvNodeRef[]) => void; reject: (error: Error) => void }>();
  constructor(private changed: (state: SttvOpening) => void,
    private createWorker: () => SttvWorkerPort) {}

  private publish(state: SttvOpening) { this.state = state; this.changed(state); }
  unsupportedDirectory() {
    this.release();
    this.publish({ ...sttvIdle, status: 'error', operationId: ++this.serial,
      error: sttvDiagnostic('directory_unsupported', null) });
  }
  private release() {
    if (this.activeApi) void fetch(`${service.prefix}/operations/${this.activeApi.jobId}/cancel`, {
      method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Sttv-Session': this.activeApi.token }, body: '{}',
    }).catch(() => undefined);
    this.activeApi = null;
    this.worker?.terminate(); this.worker = null;
    for (const request of this.pending.values()) request.reject(new Error('Database operation cancelled.'));
    this.pending.clear();
  }
  open(files: File[]) {
    if (!files.length) return;
    const operationId = ++this.serial;
    this.release();
    this.publish({ ...sttvIdle, status: 'loading', operationId, files: [...files] });
    try {
      const worker = this.createWorker();
      this.worker = worker;
      const current = () => this.serial === operationId && this.worker === worker;
      worker.onmessage = ({ data }: MessageEvent<SttvWorkerMessage>) => {
        if (!current() || data.operationId !== operationId) return;
        if (data.type === 'api_operation') { this.activeApi = data.jobId ? { jobId: data.jobId, token: data.token } : null; return; }
        if (data.type === 'loaded' || data.type === 'load_error') {
          const pending = this.pending.get(data.requestId);
          if (!pending || data.snapshotRevision !== pending.revision || data.snapshotRevision !== this.state.data?.snapshotRevision) return;
          this.pending.delete(data.requestId);
          if (data.type === 'loaded') {
            if (data.data.snapshotRevision !== pending.revision) {
              for (const request of this.pending.values()) request.reject(new Error('Database snapshot changed.'));
              this.pending.clear();
            }
            const loaded = { ...data.data, datasets: data.data.datasets.map(dataset => ({ ...dataset,
              state: [...this.pending.values()].some(r => r.kinds.includes(dataset.kind)) ? 'loading' as const : dataset.state })) };
            this.publish({ ...this.state, status: Object.values(loaded.technologies).some(t => t.tree.visibility?.visible !== false) ? 'ready' : 'empty',
              data: loaded, diagnostics: loaded.diagnostics });
            pending.resolve(data.refs);
          } else {
            this.publish({ ...this.state, data: { ...this.state.data!, coverage: data.coverage ?? this.state.data!.coverage,
              datasets: this.state.data!.datasets.map(dataset =>
              pending.kinds.includes(dataset.kind) ? { ...dataset, state: 'failed' } : dataset) },
              diagnostics: [...this.state.diagnostics, data.error] });
            pending.reject(Object.assign(new Error(String(data.error.details.reason ?? data.error.code)),
              { code: data.error.details.serviceCode ?? data.error.code }));
          }
          return;
        }
        if (this.state.status !== 'loading') return;
        if (data.type === 'progress') this.publish({ ...this.state, phase: data.phase, progress: data.file,
          members: data.file.kind ? [...this.state.members.filter(member => member.fileIndex !== data.file.fileIndex), data.file]
            : this.state.members });
        else if (data.type === 'ready') this.publish({ ...this.state,
          status: Object.values(data.data.technologies).some(t => t.tree.visibility?.visible !== false) ? 'ready' : 'empty',
          data: data.data, diagnostics: data.data.diagnostics });
        else if (data.type === 'error') {
          this.release();
          this.publish({ ...this.state, status: 'error', error: data.error, diagnostics: data.diagnostics });
        }
      };
      worker.onerror = event => {
        event.preventDefault();
        if (current()) this.fail({ message: event.message, filename: event.filename,
          line: event.lineno, column: event.colno });
      };
      worker.onmessageerror = () => { if (current()) this.fail({ message: 'Worker message could not be decoded.' }); };
      worker.postMessage({ type: 'open_database_set', operationId, files });
    } catch (error) { this.fail(sttvExceptionDetails(error)); }
  }
  loadDatasets(kinds: SttvDatabaseKind[]) { return this.request('load_datasets', { kinds }, kinds); }
  applyDlc(enabled: string[]) { return this.request('apply_dlc', { enabled }, []); }
  cancelDlc() { this.worker?.postMessage({ type: 'cancel_dlc', operationId: this.state.operationId,
    requestId: 0, snapshotRevision: this.state.data?.snapshotRevision }); }
  resolveObjects(objects: SttvObjectRef[]) { return this.request('resolve_objects', { objects }, []); }
  resolveNodes(refs: SttvNodeRef[]) { return this.request('resolve_nodes', { refs }, []); }
  private request(type: 'load_datasets' | 'resolve_objects' | 'resolve_nodes' | 'apply_dlc', payload: object, kinds: SttvDatabaseKind[]) {
    if (!this.worker || !this.state.data || !['ready', 'empty'].includes(this.state.status)) {
      return Promise.reject(new Error('Open a database set first.'));
    }
    const requestId = ++this.requestSerial, snapshotRevision = this.state.data.snapshotRevision;
    const promise = new Promise<SttvNodeRef[]>((resolve, reject) => {
      this.pending.set(requestId, { revision: snapshotRevision, kinds, resolve, reject });
    });
    this.publish({ ...this.state, data: { ...this.state.data, datasets: this.state.data.datasets.map(dataset =>
      kinds.includes(dataset.kind) ? { ...dataset, state: 'loading' } : dataset) } });
    try {
      this.worker.postMessage({ type, operationId: this.state.operationId, requestId, snapshotRevision, ...payload });
    } catch (error) { this.fail(sttvExceptionDetails(error)); }
    return promise;
  }
  private fail(details: Record<string, unknown>) {
    this.release();
    this.publish({ ...this.state, status: 'error',
      error: sttvDiagnostic('worker_failed', this.state.phase, details) });
  }
  retry() { if (this.state.status === 'error' && this.state.files.length) this.open(this.state.files); }
  cancel() { ++this.serial; this.release(); this.publish({ ...sttvIdle }); }
  dispose() { ++this.serial; this.release(); }
}

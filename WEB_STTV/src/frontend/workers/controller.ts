import type { SttvCatalog } from '../data/model';
import type { SttvDiagnostic, SttvPhase } from './diagnostics';
import { sttvDiagnostic, sttvExceptionDetails } from './diagnostics';
import type { SttvWorkerMessage, SttvFileProgress } from './protocol';

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
  constructor(private changed: (state: SttvOpening) => void,
    private createWorker: () => SttvWorkerPort) {}

  private publish(state: SttvOpening) { this.state = state; this.changed(state); }
  private release() { this.worker?.terminate(); this.worker = null; }
  open(files: File[]) {
    if (!files.length) return;
    const operationId = ++this.serial;
    this.release();
    this.publish({ ...sttvIdle, status: 'loading', operationId, files: [...files] });
    try {
      const worker = this.createWorker();
      this.worker = worker;
      const current = () => this.serial === operationId && this.worker === worker && this.state.status === 'loading';
      worker.onmessage = ({ data }: MessageEvent<SttvWorkerMessage>) => {
        if (!current() || data.operationId !== operationId) return;
        if (data.type === 'progress') this.publish({ ...this.state, phase: data.phase, progress: data.file,
          members: data.file.kind ? [...this.state.members.filter(member => member.fileIndex !== data.file.fileIndex), data.file]
            : this.state.members });
        else if (data.type === 'ready') this.publish({ ...this.state,
          status: Object.keys(data.data.technologies).length ? 'ready' : 'empty',
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
  private fail(details: Record<string, unknown>) {
    this.release();
    this.publish({ ...this.state, status: 'error',
      error: sttvDiagnostic('worker_failed', this.state.phase, details) });
  }
  retry() { if (this.state.status === 'error' && this.state.files.length) this.open(this.state.files); }
  cancel() { ++this.serial; this.release(); this.publish({ ...sttvIdle }); }
  dispose() { ++this.serial; this.release(); }
}

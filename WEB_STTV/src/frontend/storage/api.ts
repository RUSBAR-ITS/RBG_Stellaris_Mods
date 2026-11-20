import config from '../../../config/service.json';
import type { SttvManifest } from './model';
import type { SttvRemoteBytes } from './bytes';
import { sttvCheckManifest } from './manifest';

export class SttvApiError extends Error {
  constructor(readonly code: string, message: string) { super(message); }
}
export interface SttvApiJob {
  id: string; requestId: string; before: string; status: 'running' | 'completed' | 'cancelled' | 'failed';
  error: { code: string; message: string } | null;
  result: { setId: string; snapshotRevision: string; combinationId: string;
    profile: { known: string[]; enabled: string[]; catalog_revision: string }; diagnostics: unknown[] } | null;
}
export class SttvApi {
  token = '';
  active: string | null = null;
  cancelRequested = false;
  constructor(private announce: (jobId: string | null, token: string) => void = () => undefined) {}
  async request<T>(path: string, payload?: unknown): Promise<T> {
    let response: Response;
    try {
      response = await fetch(config.prefix + path, { method: payload === undefined ? 'GET' : 'POST',
        headers: { 'X-Sttv-Session': this.token, ...(payload === undefined ? {} : { 'Content-Type': 'application/json' }) },
        ...(payload === undefined ? {} : { body: JSON.stringify(payload) }) });
    } catch { throw new SttvApiError('service_unavailable', 'Local service is unavailable.'); }
    const value = await response.json().catch(() => null);
    if (!response.ok || value?.error) throw new SttvApiError(value?.error?.code ?? 'service_unavailable',
      value?.error?.message ?? 'Local service is unavailable.');
    return value as T;
  }
  async connect(manifest: SttvManifest) {
    const result = await this.request<{ token: string }>('/connect', { setId: manifest.set_id, snapshotRevision: manifest.snapshot_revision });
    this.token = result.token;
  }
  async calculate(revision: string, enabled: string[] | null, baseCombinationId: string) {
    this.cancelRequested = false;
    const requestId = crypto.randomUUID();
    let job = await this.request<SttvApiJob>('/operations', { requestId, snapshotRevision: revision, enabled, baseCombinationId });
    const identifier = job.id;
    this.active = job.id; this.announce(job.id, this.token);
    try {
      while (job.status === 'running') {
        await new Promise(resolve => setTimeout(resolve, config.poll_interval_ms));
        job = await this.request<SttvApiJob>(`/operations/${job.id}`);
        if (job.status === 'running' && this.cancelRequested) await this.cancel();
      }
      if (job.status !== 'completed' || !job.result) throw new SttvApiError(job.error?.code ?? 'cancelled', job.error?.message ?? 'Cancelled.');
      if (job.before !== revision || job.requestId !== requestId || job.id !== identifier)
        throw new SttvApiError('stale_snapshot', 'Calculation belongs to another request or snapshot.');
      return job.result;
    } finally { this.active = null; this.announce(null, this.token); }
  }
  async cancel() {
    this.cancelRequested = true;
    if (this.active) await this.request(`/operations/${this.active}/cancel`, {});
  }
  async snapshot(revision: string) {
    const manifest = sttvCheckManifest(await this.request(`/snapshots/${revision}/manifest`));
    if (manifest.snapshot_revision !== revision) throw new SttvApiError('stale_snapshot', 'Snapshot response differs.');
    const urls = new Map<string, string>();
    for (const [kind, dataset] of Object.entries(manifest.datasets)) for (const row of dataset.documents) {
      urls.set(row.path, `/snapshots/${revision}/documents/${kind}/${row.document_id}`);
    }
    for (const [id, row] of Object.entries(manifest.presentation?.files ?? {})) urls.set(row.path, `/snapshots/${revision}/images/${id}`);
    const remote: SttvRemoteBytes = async path => {
      const url = urls.get(path);
      if (!url) throw new SttvApiError('unknown_resource', 'Resource is not in the snapshot.');
      const response = await fetch(config.prefix + url, { headers: { 'X-Sttv-Session': this.token } });
      if (!response.ok || !response.body) throw new SttvApiError('resource_unavailable', 'Cannot read the published resource.');
      return { size: Number(response.headers.get('Content-Length')), stream: () => response.body! };
    };
    return { manifest, remote };
  }
}

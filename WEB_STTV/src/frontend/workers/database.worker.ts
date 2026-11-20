import { SttvStorageSession } from '../storage/session';
import { SttvPreparationError, sttvDiagnostic, sttvExceptionDetails } from './diagnostics';
import type { SttvFileProgress, SttvCommand, SttvWorkerMessage } from './protocol';
import type { SttvTargetRegistry, SttvTargetRules } from '../data/textTargets';
import opening from '../../../config/frontend/opening.json';
import type { SttvDatabaseKind } from '../data/model';
import { SttvApi, SttvApiError } from '../storage/api';
import { sttvOpenDlc } from './dlc';

const modules = import.meta.glob<SttvTargetRules>('../../../config/enrichment/targets/*.json', { eager: true, import: 'default' });
const rules = Object.fromEntries(Object.entries(modules).map(([path, value]) =>
  [path.slice(path.lastIndexOf('/') + 1, -5), value])) as SttvTargetRegistry;
const scope = globalThis as unknown as {
  onmessage: (event: MessageEvent<SttvCommand>) => void;
  postMessage: (message: SttvWorkerMessage) => void;
};
let session: SttvStorageSession | null = null, activeOperation = 0;
let api: SttvApi | null = null, service: { available: boolean; code?: string } = { available: false };
let dlcReport: Record<string, unknown> | undefined;
scope.onmessage = async ({ data: command }) => {
  const { operationId } = command;
  if (command.type !== 'open_database_set' && (operationId !== activeOperation || !session
    || command.snapshotRevision !== session.reader.manifest.snapshot_revision)) return;
  try {
    if (command.type === 'open_database_set') {
      activeOperation = operationId; session = null;
      scope.postMessage({ type: 'progress', operationId, phase: 'reading',
        file: { fileIndex: 0, total: command.files.length, kind: null, setId: null } });
      const initial = await SttvStorageSession.open(command.files, rules);
      api = new SttvApi((jobId, token) => scope.postMessage({ type: 'api_operation', operationId, jobId, token }));
      const prepared = await sttvOpenDlc(initial, rules, api);
      const opened = prepared.session;
      service = prepared.service;
      if (activeOperation !== operationId) return;
      session = opened;
      let ordinal = 0;
      const total = [...new Set(opening.initial_datasets as SttvDatabaseKind[])].reduce((count, kind) =>
        count + opened.reader.manifest.datasets[kind].documents.length, 0);
      const data = await opened.initial((kind, documentId) => {
        const file: SttvFileProgress = { fileIndex: ordinal++, total, kind,
          setId: opened.reader.manifest.set_id, documentId };
        scope.postMessage({ type: 'progress', operationId, phase: 'preparing', file });
      });
      dlcReport = prepared.report;
      data.dlcService = service; data.dlcReport = dlcReport;
      if (activeOperation === operationId) scope.postMessage({ type: 'ready', operationId, data });
    } else {
      const current = session!;
      if (command.type === 'cancel_dlc') { await api?.cancel(); return; }
      if (command.type === 'apply_dlc') {
        if (!api || !service.available) throw new SttvApiError(service.code ?? 'service_unavailable', 'Local service is unavailable.');
        const calculation = await api.calculate(command.snapshotRevision, command.enabled, current.combinationId);
        const snapshot = await api.snapshot(calculation.snapshotRevision);
        const result = await current.refresh(snapshot.manifest, calculation.combinationId, snapshot.remote);
        if (session !== current) return;
        session = result.session;
        dlcReport = calculation;
        result.data.dlcService = service; result.data.dlcReport = dlcReport;
        scope.postMessage({ type: 'loaded', operationId, requestId: command.requestId,
          snapshotRevision: command.snapshotRevision, data: result.data, refs: [] });
        return;
      }
      const result = command.type === 'load_datasets'
        ? { data: await current.load(command.kinds), refs: [] }
        : command.type === 'resolve_nodes' ? await current.resolveNodes(command.refs)
        : await current.resolve(command.objects);
      result.data.dlcService = service;
      result.data.dlcReport = dlcReport;
      if (session === current) scope.postMessage({ type: 'loaded', operationId, requestId: command.requestId,
        snapshotRevision: current.reader.manifest.snapshot_revision, ...result });
    }
  } catch (error) {
    const diagnostic = error instanceof SttvPreparationError ? error.diagnostic
      : sttvDiagnostic(error instanceof SyntaxError ? 'invalid_json' : 'worker_failed', 'preparing',
        { ...sttvExceptionDetails(error), ...(error instanceof SttvApiError ? { serviceCode: error.code, reason: error.message } : {}) });
    if (operationId !== activeOperation) return;
    if (command.type === 'open_database_set') {
      scope.postMessage({ type: 'error', operationId, error: diagnostic, diagnostics: [] });
    } else scope.postMessage({ type: 'load_error', operationId, requestId: command.requestId,
      snapshotRevision: command.snapshotRevision, error: diagnostic, coverage: session?.reader.coverage() });
  }
};

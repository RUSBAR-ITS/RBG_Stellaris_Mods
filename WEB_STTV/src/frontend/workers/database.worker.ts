import { sttvAdaptDatabase } from '../data/adapter';
import { SttvPreparationError, sttvDiagnostic, sttvExceptionDetails } from './diagnostics';
import type { SttvDiagnostic, SttvPhase } from './diagnostics';
import type { SttvOpenCommand, SttvWorkerMessage } from './protocol';

const sttvScope = globalThis as unknown as {
  database?: unknown;
  onmessage: (event: MessageEvent<SttvOpenCommand>) => void;
  postMessage: (message: SttvWorkerMessage) => void;
};
sttvScope.onmessage = async ({ data: command }) => {
  if (command.type !== 'open_database') return;
  const { operationId, file } = command;
  let phase: SttvPhase = 'reading';
  const diagnostics: SttvDiagnostic[] = [];
  function progress(next: SttvPhase) {
    phase = next;
    sttvScope.postMessage({ type: 'progress', operationId, phase });
  }
  try {
    progress('reading');
    let text = await file.text();
    progress('parsing');
    sttvScope.database = JSON.parse(text);
    text = '';
    progress('preparing');
    const data = sttvAdaptDatabase(sttvScope.database, diagnostics);
    sttvScope.postMessage({ type: 'ready', operationId, data });
  } catch (error) {
    sttvScope.database = undefined;
    const diagnostic = error instanceof SttvPreparationError ? error.diagnostic : sttvDiagnostic(
      phase === 'reading' ? 'file_read_failed' : phase === 'parsing' ? 'invalid_json' : 'worker_failed',
      phase, sttvExceptionDetails(error));
    sttvScope.postMessage({ type: 'error', operationId, error: diagnostic, diagnostics });
  }
};

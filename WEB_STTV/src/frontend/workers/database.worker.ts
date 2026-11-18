import { SttvSetAdapter } from '../data/setAdapter';
import { sttvCheckMember } from '../data/setMetadata';
import { SttvPreparationError, sttvDiagnostic, sttvExceptionDetails } from './diagnostics';
import type { SttvDiagnostic, SttvPhase } from './diagnostics';
import type { SttvFileProgress, SttvOpenCommand, SttvWorkerMessage } from './protocol';
import type { SttvTargetRegistry, SttvTargetRules } from '../data/textTargets';
import { sttvReadJson } from '../data/jsonStream';

const modules = import.meta.glob<SttvTargetRules>('../../../config/enrichment/targets/*.json', { eager: true, import: 'default' });
const rules = Object.fromEntries(Object.entries(modules).map(([path, value]) =>
  [path.slice(path.lastIndexOf('/') + 1, -5), value])) as SttvTargetRegistry;
const sttvScope = globalThis as unknown as {
  files?: File[];
  onmessage: (event: MessageEvent<SttvOpenCommand>) => void;
  postMessage: (message: SttvWorkerMessage) => void;
};
sttvScope.onmessage = async ({ data: command }) => {
  if (command.type !== 'open_database_set') return;
  const { operationId, files } = command;
  sttvScope.files = files;
  let phase: SttvPhase = 'reading';
  let file: SttvFileProgress = { fileIndex: 0, total: files.length, kind: null, setId: null };
  const diagnostics: SttvDiagnostic[] = [];
  function progress(next: SttvPhase) {
    phase = next;
    sttvScope.postMessage({ type: 'progress', operationId, phase, file });
  }
  try {
    const adapter = new SttvSetAdapter(files, rules, diagnostics);
    for (const [fileIndex, input] of files.entries()) {
      file = { fileIndex, total: files.length, kind: null, setId: null };
      progress('reading');
      progress('parsing');
      const { metadata, documentCount } = await sttvReadJson(input);
      file = { ...file, ...sttvCheckMember(metadata, fileIndex) };
      adapter.begin(metadata, fileIndex);
      adapter.metadata.datasets.at(-1)!.documentCount = documentCount;
      progress('preparing');
      await sttvReadJson(input, (document, index) => {
        adapter.document({ ...metadata, documents: [document] }, fileIndex, index);
      });
    }
    sttvScope.postMessage({ type: 'ready', operationId, data: adapter.finish() });
  } catch (error) {
    const diagnostic = error instanceof SttvPreparationError ? error.diagnostic : sttvDiagnostic(
      error instanceof SyntaxError ? 'invalid_json' : phase === 'reading' || phase === 'parsing'
        ? 'file_read_failed' : 'worker_failed',
      phase, sttvExceptionDetails(error));
    diagnostic.details.file ??= { ...file, name: files[file.fileIndex]?.name ?? null };
    sttvScope.postMessage({ type: 'error', operationId, error: diagnostic, diagnostics });
  }
};

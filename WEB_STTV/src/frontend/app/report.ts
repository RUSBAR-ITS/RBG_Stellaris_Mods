import type { SttvOpening } from '../workers/controller';

export function sttvBuildReport(state: SttvOpening, now = new Date()) {
  if (!state.file || !['ready', 'empty', 'error'].includes(state.status)) throw new Error('No completed attempt.');
  return { format: 'sttv.frontend_diagnostics', formatVersion: 1, exportedAt: now.toISOString(),
    operationId: state.operationId, file: { name: state.file.name, size: state.file.size },
    result: state.status, error: state.error, diagnostics: state.diagnostics };
}
export function sttvDownloadReport(state: SttvOpening) {
  const report = sttvBuildReport(state);
  const url = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' }));
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `sttv-report-${report.exportedAt.replaceAll(':', '-')}-${report.operationId}.json`;
  document.body.append(anchor);
  try { anchor.click(); } finally {
    anchor.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
}

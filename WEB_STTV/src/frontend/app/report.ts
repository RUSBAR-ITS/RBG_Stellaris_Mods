import type { SttvOpening } from '../workers/controller';

export function sttvBuildReport(state: SttvOpening, now = new Date()) {
  if (!state.files.length || !['ready', 'empty', 'error'].includes(state.status)) throw new Error('No completed attempt.');
  return { format: 'sttv.frontend_diagnostics', formatVersion: 2, exportedAt: now.toISOString(),
    operationId: state.operationId, setId: state.data?.setId ?? null,
    files: state.files.map((file, fileIndex) => {
      const member = state.members.find(item => item.fileIndex === fileIndex);
      const dataset = state.data?.datasets.find(item => item.fileIndex === fileIndex);
      return { name: file.name, size: file.size, fileIndex, kind: dataset?.kind ?? member?.kind ?? null,
        setId: state.data?.setId ?? member?.setId ?? null };
    }),
    counts: state.data ? { technologies: Object.keys(state.data.technologies).length,
      components: Object.keys(state.data.components).length, buildings: Object.keys(state.data.buildings).length,
      objectRequirements: state.data.objectRequirements.length, objectUpgrades: state.data.objectUpgrades.length,
      upgradeEvidence: state.data.upgradeEvidence.length } : null,
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

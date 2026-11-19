import type { SttvOpening } from '../workers/controller';
import type { SttvLayoutReport } from '../data/tree/model';

export function sttvBuildReport(state: SttvOpening, now = new Date(), tree?: SttvLayoutReport) {
  if (!state.files.length || !['ready', 'empty', 'error'].includes(state.status)) throw new Error('No completed attempt.');
  return { format: 'sttv.frontend_diagnostics', formatVersion: 4, exportedAt: now.toISOString(),
    tree: tree ?? null, treeCombination: state.data?.treeCombination ?? null,
    operationId: state.operationId, root: state.files[0]?.webkitRelativePath?.split('/')[0] || null, setId: state.data?.setId ?? null,
    snapshotRevision: state.data?.snapshotRevision ?? null, coverage: state.data?.coverage ?? null,
    datasets: state.data?.datasets ?? [],
    files: state.files.map((file, fileIndex) => {
      return { name: file.name, path: file.webkitRelativePath, size: file.size, fileIndex };
    }),
    counts: state.data ? { technologies: Object.keys(state.data.technologies).length,
      components: state.data.datasets.find(d => d.kind === 'components')?.state === 'loaded' ? Object.keys(state.data.components).length : null,
      buildings: state.data.datasets.find(d => d.kind === 'buildings')?.state === 'loaded' ? Object.keys(state.data.buildings).length : null,
      objectRequirements: state.data.objectRequirements.length, objectUpgrades: state.data.objectUpgrades.length,
      upgradeEvidence: state.data.upgradeEvidence.length } : null,
    result: state.status, error: state.error, diagnostics: state.diagnostics };
}
export function sttvDownloadReport(state: SttvOpening, tree?: SttvLayoutReport) {
  const report = sttvBuildReport(state, new Date(), tree);
  const url = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' }));
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `sttv-report-${report.exportedAt.replaceAll(':', '-')}-${report.operationId}.json`;
  document.body.append(anchor);
  try { anchor.click(); } finally {
    anchor.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
}

import { SttvApi, SttvApiError } from '../storage/api';
import { SttvStorageSession } from '../storage/session';
import type { SttvTargetRegistry } from '../data/textTargets';
import type { SttvManifest } from '../storage/model';
import { sttvRecord } from '../data/tree/contract';
import { sttvTreeCombination } from '../data/tree/metadata';
import layout from '../../../config/frontend/tree_layout.json';

export function sttvAllDlcCombination(manifest: SttvManifest) {
  const tree = manifest.technology_tree;
  if (!sttvRecord(tree) || !sttvRecord(tree.combinations)) return undefined;
  const base = sttvTreeCombination(manifest, layout.combination_id);
  return Object.keys(tree.combinations).find(id => {
    const candidate = sttvTreeCombination(manifest, id), dlc = candidate.parameters.dlc;
    return dlc && dlc.known.length === dlc.enabled.length && dlc.known.every(v => dlc.enabled.includes(v))
      && Object.entries(base.parameters.variants).every(([key, value]) => candidate.parameters.variants[key] === value);
  });
}

export async function sttvOpenDlc(opened: SttvStorageSession, rules: SttvTargetRegistry, api: SttvApi) {
  const original = opened.reader.manifest;
  try { await api.connect(original); }
  catch (error) {
    const ready = sttvAllDlcCombination(original);
    if (!ready) throw error;
    return { session: SttvStorageSession.fromSnapshot(original, opened.reader.files, rules, ready),
      service: { available: false, code: error instanceof SttvApiError ? error.code : 'service_unavailable' } };
  }
  const result = await api.calculate(original.snapshot_revision, null, layout.combination_id);
  const { manifest, remote } = await api.snapshot(result.snapshotRevision);
  if (manifest.set_id !== original.set_id) throw new SttvApiError('set_mismatch', 'Calculation belongs to another set.');
  return { session: SttvStorageSession.fromSnapshot(manifest, opened.reader.files, rules, result.combinationId, remote),
    service: { available: true }, report: result };
}

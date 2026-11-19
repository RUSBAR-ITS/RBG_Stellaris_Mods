import settings from '../../../../config/frontend/tree_layout.json';
import type { SttvManifest } from '../../storage/model';
import type { SttvTreeCombination } from './model';
import { sttvRecord, sttvTreeError } from './contract';

export function sttvTreeCombination(manifest: SttvManifest, id = settings.combination_id): SttvTreeCombination {
  const metadata = manifest.technology_tree;
  if (!sttvRecord(metadata) || metadata.format_version !== 1 || !sttvRecord(metadata.combinations)
    || !Object.hasOwn(metadata.combinations, id)) {
    sttvTreeError('tree_combination_missing', 'Missing combination or unsupported enrichment version.', { combinationId: id });
  }
  const row = metadata.combinations[id];
  const invalid = (reason: string): never => sttvTreeError('tree_enrichment_invalid', reason, { combinationId: id });
  if (!sttvRecord(row) || row.mode !== 'reference' || !sttvRecord(row.parameters)
    || row.parameters.mode !== row.mode || !sttvRecord(row.parameters.profile)
    || !sttvRecord(row.parameters.variants) || !Object.values(row.parameters.variants).every(v => typeof v === 'string')) {
    return invalid('Invalid combination parameters.');
  }
  const revisions = ['input_revision', 'rules_revision', 'parameters_revision', 'calculation_revision', 'result_revision'] as const;
  for (const key of revisions) if (typeof row[key] !== 'string' || !/^[a-f0-9]{64}$/.test(row[key])) invalid(`Invalid ${key}.`);
  if (typeof row.implementation_revision !== 'string' || !row.implementation_revision
    || !Array.isArray(row.inputs) || !row.inputs.length) return invalid('Missing input revisions.');
  const kinds = new Set<string>();
  for (const input of row.inputs) {
    if (!sttvRecord(input) || typeof input.kind !== 'string' || kinds.has(input.kind)
      || !Object.hasOwn(manifest.datasets, input.kind) || input.algorithm !== 'sttv.dataset_sources.v1') {
      return invalid('Invalid or duplicated combination input.');
    }
    kinds.add(input.kind);
    const dataset = manifest.datasets[input.kind as keyof typeof manifest.datasets];
    if (input.hash !== dataset.source_revision) sttvTreeError('tree_combination_stale', 'Dataset source revision mismatch.',
      { combinationId: id, kind: input.kind, expected: dataset.source_revision, received: input.hash });
  }
  if (!kinds.has('technologies')) return invalid('Technology input is missing.');
  if (row.source_set_id !== manifest.set_id) sttvTreeError('tree_combination_stale', 'Source set ID mismatch.',
    { combinationId: id, expected: manifest.set_id, received: row.source_set_id });
  // Keep only the metadata needed by the field and report, not the rules snapshot.
  return { id, mode: row.mode, parameters: row.parameters as SttvTreeCombination['parameters'],
    source_set_id: manifest.set_id, inputs: row.inputs as SttvTreeCombination['inputs'],
    implementation_revision: row.implementation_revision,
    ...Object.fromEntries(revisions.map(key => [key, row[key]])) } as SttvTreeCombination;
}

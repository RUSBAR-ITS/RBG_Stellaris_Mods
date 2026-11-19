import type { SttvTreeCombination } from '../../src/frontend/data/tree/model';
import type { SttvNode } from '../../src/frontend/data/syntax';

export function sttvCombination(ids: string[], variants: Record<string, string> = {}): SttvTreeCombination {
  return { id: 'reference_default', mode: 'reference',
    parameters: { mode: 'reference', profile: {}, variants: Object.fromEntries(ids.map(id => [id, variants[id] ?? 'base'])) },
    source_set_id: 'a'.repeat(64), inputs: [{ kind: 'technologies', algorithm: 'sttv.dataset_sources.v1', hash: 'c'.repeat(64) }],
    implementation_revision: 'fixture', input_revision: 'd'.repeat(64), rules_revision: 'e'.repeat(64),
    parameters_revision: 'f'.repeat(64), calculation_revision: '1'.repeat(64), result_revision: '2'.repeat(64) };
}
export function sttvConnect(nodes: SttvNode[], parents: Record<string, string | null>, combinationId = 'reference_default') {
  const rows = Object.fromEntries(nodes.map(node => [node.key!.text!, { parent_tech: parents[node.key!.text!] ?? null,
    status: parents[node.key!.text!] ? 'resolved' : 'root', children: [] as string[] }]));
  for (const [id, row] of Object.entries(rows)) if (row.parent_tech) rows[row.parent_tech].children.push(id);
  for (const node of nodes) node.enrichments = { ...node.enrichments, technology_tree: { [combinationId]: rows[node.key!.text!] } };
}

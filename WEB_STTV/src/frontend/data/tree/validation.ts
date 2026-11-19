import type { SttvTechnology } from '../model';
import type { SttvTreeCombination } from './model';
import { sttvTreeError } from './contract';

export function sttvValidateTree(technologies: Record<string, SttvTechnology>, combination: SttvTreeCombination) {
  const selected = combination.parameters.variants;
  const fail = (reason: string, id?: string): never => sttvTreeError('tree_enrichment_invalid', reason,
    { combinationId: combination.id, technologyId: id, sourceRef: id ? technologies[id]?.sourceRef : undefined });
  for (const id of Object.keys(selected)) if (!Object.hasOwn(technologies, id)) fail('Variant entry refers to an unknown technology.', id);
  for (const tech of Object.values(technologies)) {
    if (!Object.hasOwn(selected, tech.id) || !tech.representations.some(view => view.id === selected[tech.id])) {
      fail('Missing or unknown selected representation.', tech.id);
    }
    const parent = tech.tree.parent_tech;
    if (parent !== null && (!Object.hasOwn(technologies, parent) || !technologies[parent].tree.children.includes(tech.id))) {
      fail('Missing parent or reciprocal child reference.', tech.id);
    }
    for (const child of tech.tree.children) {
      if (!Object.hasOwn(technologies, child) || technologies[child].tree.parent_tech !== tech.id) {
        fail('Missing child or reciprocal parent reference.', tech.id);
      }
    }
  }
  // Follow parent paths iteratively, including links across research areas.
  const completed = new Set<string>();
  for (const id of Object.keys(technologies)) {
    const path = new Set<string>();
    let current: string | null = id;
    while (current !== null && !completed.has(current)) {
      if (path.has(current)) fail('Cycle in the saved parent graph.', current);
      path.add(current); current = technologies[current].tree.parent_tech;
    }
    for (const member of path) completed.add(member);
  }
}

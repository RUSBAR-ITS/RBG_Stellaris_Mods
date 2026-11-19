import adapter from '../../../../config/frontend/adapter.json';
import type { SttvArea, SttvTechnology } from '../model';
import { sttvRepresentation } from './comparison';
import type { SttvTreeSettings } from './model';

export function sttvForest(technologies: Record<string, SttvTechnology>, selected: Record<string, string>, settings: SttvTreeSettings) {
  const nodes = new Map(Object.values(technologies).map(tech => {
    const rule = settings.repeatable;
    const repeated = tech.levels === rule.levels && tech.tier === rule.game_tier
      && (!rule.requires_prerequisite || tech.prerequisiteIds.length > 0);
    return [tech.id, { area: sttvRepresentation(tech, selected).area, column: repeated ? rule.display_tier : tech.tier,
      children: [] as string[] }];
  }));
  const roots = new Map((adapter.areas as SttvArea[]).map(area => [area, [] as string[]]));
  let hiddenCrossAreaLinks = 0;
  for (const tech of Object.values(technologies)) {
    const node = nodes.get(tech.id)!;
    const parent = tech.tree.parent_tech === null ? null : nodes.get(tech.tree.parent_tech)!;
    if (!parent || parent.area !== node.area) {
      roots.get(node.area)!.push(tech.id);
      if (parent) hiddenCrossAreaLinks++;
    }
    node.children = tech.tree.children.filter(child => nodes.get(child)!.area === node.area);
  }
  return { nodes, roots, hiddenCrossAreaLinks };
}

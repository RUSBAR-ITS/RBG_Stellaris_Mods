import config from '../../../config/frontend/interface.json';
import adapter from '../../../config/frontend/adapter.json';
import type { SttvArea, SttvTechnology } from './model';
import { sttvInvalid } from '../workers/diagnostics';

export interface SttvColumn { tier: number; ids: string[] }
export interface SttvAreaLayout { area: SttvArea; columns: SttvColumn[]; height: number }
export interface SttvLayout { areas: SttvAreaLayout[]; width: number; height: number }
export function sttvCompare(left: string, right: string) { return left < right ? -1 : left > right ? 1 : 0; }
export function sttvRepresentation(technology: SttvTechnology, selected: Record<string, string>) {
  return technology.representations.find(item => item.id === selected[technology.id]) ?? technology.representations[0];
}
export function sttvOrderColumn(technologies: SttvTechnology[]) {
  const pending = new Map(technologies.map(technology => [technology.id, technology]));
  const signature = (technology: SttvTechnology) => JSON.stringify([...technology.prerequisiteIds].sort(sttvCompare));
  const compare = (a: SttvTechnology, b: SttvTechnology) => a.requirementCount - b.requirementCount
    || sttvCompare(signature(a), signature(b)) || sttvCompare(a.id, b.id);
  const result: string[] = [];
  while (pending.size) {
    const available = [...pending.values()].filter(item => !item.prerequisiteIds.some(id => pending.has(id)));
    if (!available.length) throw sttvInvalid('/prerequisites', 'Cyclic dependencies prevent vertical ordering.');
    available.sort(compare);
    result.push(available[0].id);
    pending.delete(available[0].id);
  }
  return result;
}
export function sttvLayout(technologies: Record<string, SttvTechnology>, selected: Record<string, string>): SttvLayout {
  const all = Object.values(technologies);
  const lastTier = Math.max(0, ...all.map(technology => technology.tier));
  const tiers = Array.from({ length: lastTier + 1 }, (_, index) => index);
  const areas = (adapter.areas as SttvArea[]).map(area => {
    const columns = tiers.map(tier => ({ tier, ids: sttvOrderColumn(all.filter(technology =>
      technology.tier === tier && sttvRepresentation(technology, selected).area === area)) }));
    const count = Math.max(0, ...columns.map(column => column.ids.length));
    return { area, columns, height: config.areaHeadingHeight + config.tierHeadingHeight
      + count * config.cardHeight + Math.max(0, count - 1) * config.cardGap };
  });
  return { areas, width: config.fieldPadding * 2 + tiers.length * config.cardWidth + lastTier * config.columnGap,
    height: config.fieldPadding * 2 + areas.reduce((sum, area) => sum + area.height, 0)
      + (areas.length - 1) * config.areaGap };
}

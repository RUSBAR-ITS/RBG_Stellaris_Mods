import type { SttvDatabase, SttvNode } from '../../src/frontend/data/syntax';
import type { SttvArea } from '../../src/frontend/data/model';
import type { SttvStoredLocalization } from '../../src/frontend/localization/model';

export const sttvScalar = (text: string): SttvNode => ({ kind: 'scalar', text });
export const sttvBlock = (items: SttvNode[]): SttvNode => ({ kind: 'block', items });
export const sttvAssignment = (key: string, value: SttvNode): SttvNode =>
  ({ kind: 'assignment', key: sttvScalar(key), operator: '=', value });
export const sttvLogical = (operator: string, items: SttvNode[]): SttvNode =>
  ({ kind: 'logical_operation', operator, body: sttvBlock(items) });
export function sttvLocalization(id: string, text: string | null = id): SttvStoredLocalization {
  const value = (key: string, content: string | null) => ({ requested_key: key, key,
    text: content, raw: content, source: null, inherited_from: null, unresolved_references: [] });
  return { ru: { name: value(id, text), description: value(`${id}_desc`, text === null ? null : `${text} details`) },
    en: { name: value(id, text), description: value(`${id}_desc`, text === null ? null : `${text} details`) } };
}
export function sttvTechnology(id: string, tier = 0, area: SttvArea = 'physics', requirements: SttvNode[] = []) {
  return { ...sttvAssignment(id, sttvBlock([
    sttvAssignment('area', sttvScalar(area)), sttvAssignment('tier', sttvScalar(String(tier))),
    sttvAssignment('prerequisites', sttvBlock(requirements)),
  ])), enrichments: { localization: sttvLocalization(id) } };
}
export function sttvVariant(id: string, area?: SttvArea, text = id): SttvNode {
  return { ...sttvAssignment('technology_swap', sttvBlock(area ? [sttvAssignment('area', sttvScalar(area))] : [])),
    enrichments: { localization: sttvLocalization(id, text) } };
}
export function sttvDatabase(items: SttvNode[]): SttvDatabase {
  return { format: 'sttv.parse_database', format_version: 4,
    documents: [{ source: { file: 'common/technology/example.txt', root: 'STELLARIS_ROOT' }, items }] };
}
export function sttvBrowserDatabase() {
  const base = sttvTechnology('tech_example');
  base.value!.items!.push(sttvVariant('tech_example', 'society'), sttvVariant('tech_example', 'engineering'));
  const items = [base, sttvTechnology('tech_child', 0, 'physics', [sttvScalar('tech_example')]),
    ...Array.from({ length: 15 }, (_, i) => sttvTechnology(`tech_tall_${i}`, 1)),
    sttvTechnology('tech_wide', 5)];
  return sttvDatabase(items);
}

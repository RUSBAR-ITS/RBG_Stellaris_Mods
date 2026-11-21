import dimensions from '../../../config/frontend/interface.json';
import { sttvConnectAreas } from '../data/connections/layout';
import type { SttvArea, SttvCardCatalog, SttvNodeRef } from '../data/model';
import type { SttvLanguage, SttvLocalizationIndex } from '../localization/model';

export const referenceEndpoint = '/api/trees/reference';
export interface ReferenceNode {
  _id: string; area: SttvArea; parent_tech: string | null; children: string[];
  location: Record<SttvLanguage, [number, number]>;
}
interface Card {
  tier: number; levels: number | null; cost: number | null; weight: number | null; rare: boolean; dangerous: boolean;
  starting: boolean; categories: string[]; name: string; description: string; icon: string; source: SttvNodeRef;
}
interface TreeResponse { tree_id: string; enabled_dlc: string[]; items: ReferenceNode[]; cards: Record<string, Card> }
export interface ServerDlc { id: string; name: Record<SttvLanguage, string>; thumbnail: string | null }
const areas: SttvArea[] = ['physics', 'society', 'engineering'];

export async function request<T>(url: string, method = 'GET', body?: unknown, signal?: AbortSignal): Promise<T> {
  const response = await fetch(url, { method, signal, headers: body === undefined ? {} : { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body) });
  if (!response.ok) {
    const info = await response.json().catch(() => ({}));
    throw new Error(info.reason || info.error || String(response.status));
  }
  return response.json();
}

export async function fetchReference(enabled?: string[]) {
  const result = await request<TreeResponse>(referenceEndpoint, 'POST', enabled ? { enabled_dlc: enabled } : {});
  const technologies: SttvCardCatalog['technologies'] = {}, variants: Record<string, string> = {};
  const keys = new Set<string>();
  function icon(group: string, id: string) {
    return /^[a-z0-9_-]+$/i.test(id) ? group + '/' + id + '.png' : null;
  }
  for (const node of result.items) {
    const id = node._id, c = result.cards[id];
    [c.name, c.description, ...c.categories].forEach(key => keys.add(key));
    variants[id] = 'base';
    technologies[id] = { id, tier: c.tier, levels: c.levels, cost: c.cost, weight: c.weight, rare: c.rare,
      dangerous: c.dangerous, startTech: c.starting, sourceRef: c.source, representations: [{ id: 'base',
        nameId: c.name, descriptionId: c.description, categories: c.categories, area: node.area, sourceRef: c.source,
        iconAssetId: icon('gfx/interface/icons/technologies', c.icon) }] };
  }
  const localization: SttvLocalizationIndex = { ru: {}, en: {} };
  await Promise.all((['ru', 'en'] as const).map(async language => {
    const result = await request<{ items: { key: string; text: string | null }[] }>('/api/localization/lookup', 'POST', { language, keys: [...keys] });
    for (const { key, text } of result.items) localization[language][key] = { text, status: text === null ? 'missing' : 'resolved' };
  }));
  const data: SttvCardCatalog = { technologies, treeCombination: { parameters: { variants } },
    presentation: { research_icons: Object.fromEntries(areas.map(a => [a, icon('gfx/interface/icons/resources', a + '_research')])) } };
  return { id: result.tree_id, enabled: result.enabled_dlc, nodes: result.items, localization, data };
}

export function referenceLayout(nodes: ReferenceNode[], language: SttvLanguage, cardHeight: number) {
  const byId = new Map(nodes.map(n => [n._id, n]));
  const parents = Object.fromEntries(nodes.map(n => [n._id, n.parent_tech]));
  const count = 1 + Math.max(0, ...nodes.map(n => n.location[language][0]));
  const tiers = Array.from({ length: count }, (_, i) => i);
  const byRow = (a: ReferenceNode, b: ReferenceNode) => a.location[language][1] - b.location[language][1];
  const groups = areas.map(area => {
    const roots = nodes.filter(n => n.area === area && byId.get(n.parent_tech ?? '')?.area !== area).sort(byRow);
    const stack = [...roots].reverse(), cards = [];
    while (stack.length) {
      const n = stack.pop()!, [column, row] = n.location[language];
      cards.push({ id: n._id, column, row });
      const children = n.children.map(id => byId.get(id)!).filter(c => c.area === area).sort(byRow);
      stack.push(...children.reverse());
    }
    return { area, roots: roots.map(n => n._id), cards, rowCount: 1 + Math.max(-1, ...cards.map(c => c.row)) };
  });
  const result = sttvConnectAreas(groups, parents, count, undefined, { ...dimensions, cardHeight });
  const height = dimensions.fieldPadding * 2 + result.areas.reduce((n, a) => n + a.height, 0) + (areas.length - 1) * dimensions.areaGap;
  return { areas: result.areas, width: result.width, columns: result.columns, height, tiers };
}

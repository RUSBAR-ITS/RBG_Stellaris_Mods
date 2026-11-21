import dimensions from '../../../config/frontend/interface.json';
import { sttvConnectAreas } from '../data/connections/layout';
import type { SttvArea, SttvCardCatalog, SttvNodeRef } from '../data/model';
import type { SttvLanguage, SttvLocalizationIndex } from '../localization/model';

export const referenceEndpoint = '/api/trees/reference';
interface LayoutNode {
  _id: string; area: SttvArea; layout_area: SttvArea; parent_tech: string | null; event_only: boolean;
  location: Record<SttvLanguage, [number, number]>;
}
export interface ReferenceNode extends LayoutNode { children: string[] }
export interface TreeModes { mixed_trees: boolean; hide_event_technologies: boolean }
export const defaultModes: TreeModes = { mixed_trees: false, hide_event_technologies: false };
interface Card {
  tier: number; levels: number | null; cost: number | null; weight: number | null; rare: boolean; dangerous: boolean;
  starting: boolean; categories: string[]; name: string; description: string; icon: string; source: SttvNodeRef;
}
interface TreeResponse extends TreeModes { tree_id: string; enabled_dlc: string[]; items: ReferenceNode[];
  hidden_layout: LayoutNode[]; cards: Record<string, Card> }
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

export async function fetchReference(enabled: string[] | undefined, modes: TreeModes) {
  const result = await request<TreeResponse>(referenceEndpoint, 'POST', { enabled_dlc: enabled, ...modes });
  const technologies: SttvCardCatalog['technologies'] = {}, variants: Record<string, string> = {};
  const keys = new Set<string>();
  function icon(group: string, id: string) {
    return /^[a-z0-9_-]+$/i.test(id) ? group + '/' + id + '.png' : null;
  }
  // Measure the same population in both filter states, including a hidden tallest title.
  for (const node of [...result.items, ...result.hidden_layout]) {
    const id = node._id, c = result.cards[id];
    [c.name, c.description, ...c.categories].forEach(key => keys.add(key));
    variants[id] = 'base';
    technologies[id] = { id, tier: c.tier, levels: c.levels, cost: c.cost, weight: c.weight, rare: c.rare,
      dangerous: c.dangerous, eventOnly: node.event_only,
      startTech: c.starting, sourceRef: c.source, representations: [{ id: 'base',
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
  return { id: result.tree_id, enabled: result.enabled_dlc, nodes: result.items, hidden: result.hidden_layout,
    modes: { mixed_trees: result.mixed_trees, hide_event_technologies: result.hide_event_technologies }, localization, data };
}

export function referenceLayout(shown: ReferenceNode[], hidden: LayoutNode[], language: SttvLanguage, cardHeight: number) {
  const nodes = [...shown, ...hidden];
  const byId = new Map(nodes.map(n => [n._id, n]));
  const visible = new Set(shown.map(n => n._id));
  const descendants = new Map<string, LayoutNode[]>();
  for (const n of nodes) {
    if (!n.parent_tech || byId.get(n.parent_tech)?.layout_area !== n.layout_area) continue;
    if (!descendants.has(n.parent_tech)) descendants.set(n.parent_tech, []);
    descendants.get(n.parent_tech)!.push(n);
  }
  const parents = Object.fromEntries(nodes.map(n => [n._id, n.parent_tech]));
  const count = 1 + Math.max(0, ...nodes.map(n => n.location[language][0]));
  const tiers = Array.from({ length: count }, (_, i) => i);
  const byRow = (a: LayoutNode, b: LayoutNode) => a.location[language][1] - b.location[language][1];
  const groups = areas.map(area => {
    const roots = nodes.filter(n => n.layout_area === area && byId.get(n.parent_tech ?? '')?.layout_area !== area).sort(byRow);
    const stack = [...roots].reverse(), cards = [];
    while (stack.length) {
      const n = stack.pop()!, [column, row] = n.location[language];
      cards.push({ id: n._id, column, row });
      const children = (descendants.get(n._id) ?? []).sort(byRow);
      stack.push(...children.reverse());
    }
    return { area, roots: roots.map(n => n._id), cards, rowCount: 1 + Math.max(-1, ...cards.map(c => c.row)) };
  });
  const result = sttvConnectAreas(groups, parents, count, undefined, { ...dimensions, cardHeight }, visible);
  const height = dimensions.fieldPadding * 2 + result.areas.reduce((n, a) => n + a.height, 0) + (areas.length - 1) * dimensions.areaGap;
  return { areas: result.areas, width: result.width, columns: result.columns, height, tiers };
}

import defaultDimensions from '../../../../config/frontend/interface.json';
import defaults from '../../../../config/frontend/tree_layout.json';
import connectionSettings from '../../../../config/frontend/connections.json';
import type { SttvCatalog } from '../model';
import type { SttvLanguage } from '../../localization/model';
import type { SttvLayout, SttvTreeSettings } from './model';
import { sttvTreeComparators } from './comparison';
import { sttvForest } from './forest';
import { sttvPlaceTrees } from './placement';
import { sttvTreeError } from './contract';
import { SttvPreparationError, sttvDiagnostic } from '../../workers/diagnostics';
import { sttvCreateTextLookup } from '../../localization/sources';
import { sttvConnectAreas } from '../connections/layout';

export function sttvLayout(data: Pick<SttvCatalog, 'technologies' | 'treeCombination' | 'localization'>,
  language: SttvLanguage, settings: SttvTreeSettings = defaults, dimensions = defaultDimensions): SttvLayout {
  const started = performance.now();
  const { technologies, treeCombination: combination } = data;
  if (combination.id !== settings.combination_id) {
    sttvTreeError('tree_enrichment_invalid', 'Field configuration and loaded combination differ.',
      { expected: settings.combination_id, received: combination.id });
  }
  const selected = combination.parameters.variants;
  const compare = sttvTreeComparators(technologies, selected, language, settings, sttvCreateTextLookup(data, language));
  const forest = sttvForest(technologies, selected, settings);
  const maxTier = Math.max(0, ...[...forest.nodes.values()].map(node => node.column));
  const tiers = Array.from({ length: maxTier + 1 }, (_, tier) => tier);
  const logicalAreas = [...forest.roots].map(([area, unsorted]) => {
    const roots = [...unsorted].sort(compare.roots);
    const placed = sttvPlaceTrees(roots, forest.nodes, compare.children);
    return { area, roots, ...placed, height: dimensions.areaHeadingHeight + dimensions.tierHeadingHeight
      + placed.rowCount * dimensions.cardHeight + Math.max(0, placed.rowCount - 1) * dimensions.cardGap };
  });
  const cards = logicalAreas.flatMap(area => area.cards);
  if (cards.length !== Object.keys(technologies).length || new Set(cards.map(card => card.id)).size !== cards.length) {
    sttvTreeError('tree_layout_failed', 'The field does not cover every technology exactly once.', { combinationId: combination.id });
  }
  let connected: ReturnType<typeof sttvConnectAreas<(typeof logicalAreas)[number]>>;
  try {
    connected = sttvConnectAreas(logicalAreas, Object.fromEntries(Object.values(technologies).map(t => [t.id, t.tree.parent_tech])), tiers.length, connectionSettings, dimensions);
  } catch (error) {
    if (error instanceof SttvPreparationError) Object.assign(error.diagnostic.details,
      { combination, language, layoutSettings: settings, routingSettings: connectionSettings });
    throw error;
  }
  const { areas, width, columns } = connected;
  const height = dimensions.fieldPadding * 2 + areas.reduce((sum, area) => sum + area.height, 0)
    + Math.max(0, areas.length - 1) * dimensions.areaGap;
  const report = { combination, language, settings,
    areas: areas.map(area => ({ area: area.area, technologies: area.cards.length, trees: area.roots.length, rows: area.rowCount })),
    hiddenCrossAreaLinks: forest.hiddenCrossAreaLinks, columns: tiers.length, width, height,
    seconds: (performance.now() - started) / 1000, connections: connected.report };
  const diagnostics = Object.values(technologies).filter(tech => tech.tree.status === 'ambiguous').map(tech =>
    sttvDiagnostic('tree_ambiguous', 'preparing', { technologyId: tech.id, sourceRef: tech.sourceRef,
      combination, language, settings }));
  return { areas, tiers, columns, width, height, report, diagnostics };
}

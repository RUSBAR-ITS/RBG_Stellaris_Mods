import dimensions from '../../../../config/frontend/interface.json';
import defaults from '../../../../config/frontend/tree_layout.json';
import type { SttvCatalog } from '../model';
import type { SttvLanguage } from '../../localization/model';
import type { SttvLayout, SttvTreeSettings } from './model';
import { sttvTreeComparators } from './comparison';
import { sttvForest } from './forest';
import { sttvPlaceTrees } from './placement';
import { sttvTreeError } from './contract';
import { sttvDiagnostic } from '../../workers/diagnostics';
import { sttvCreateTextLookup } from '../../localization/sources';

export function sttvLayout(data: Pick<SttvCatalog, 'technologies' | 'treeCombination' | 'localization'>,
  language: SttvLanguage, settings: SttvTreeSettings = defaults): SttvLayout {
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
  const areas = [...forest.roots].map(([area, unsorted]) => {
    const roots = [...unsorted].sort(compare.roots);
    const placed = sttvPlaceTrees(roots, forest.nodes, compare.children);
    return { area, roots, ...placed, height: dimensions.areaHeadingHeight + dimensions.tierHeadingHeight
      + placed.rowCount * dimensions.cardHeight + Math.max(0, placed.rowCount - 1) * dimensions.cardGap };
  });
  const cards = areas.flatMap(area => area.cards);
  if (cards.length !== Object.keys(technologies).length || new Set(cards.map(card => card.id)).size !== cards.length) {
    sttvTreeError('tree_layout_failed', 'The field does not cover every technology exactly once.', { combinationId: combination.id });
  }
  const width = dimensions.fieldPadding * 2 + tiers.length * dimensions.cardWidth + maxTier * dimensions.columnGap;
  const height = dimensions.fieldPadding * 2 + areas.reduce((sum, area) => sum + area.height, 0)
    + Math.max(0, areas.length - 1) * dimensions.areaGap;
  const report = { combination, language, settings,
    areas: areas.map(area => ({ area: area.area, technologies: area.cards.length, trees: area.roots.length, rows: area.rowCount })),
    hiddenCrossAreaLinks: forest.hiddenCrossAreaLinks, columns: tiers.length, width, height,
    seconds: (performance.now() - started) / 1000 };
  const diagnostics = Object.values(technologies).filter(tech => tech.tree.status === 'ambiguous').map(tech =>
    sttvDiagnostic('tree_ambiguous', 'preparing', { technologyId: tech.id, sourceRef: tech.sourceRef,
      combination, language, settings }));
  return { areas, tiers, width, height, report, diagnostics };
}

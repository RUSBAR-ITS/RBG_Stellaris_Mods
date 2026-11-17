import config from '../../../config/frontend/adapter.json';
import { sttvFields, sttvField, sttvItems, sttvScalar } from './syntax';
import type { SttvDatabase, SttvNode } from './syntax';
import type { SttvArea, SttvCatalog, SttvRepresentation } from './model';
import { sttvRequirements } from './requirements';
import { sttvOrderColumn } from './layout';
import { SttvIndexBuilder } from '../localization/index';
import { SttvPreparationError, sttvDiagnostic, sttvInvalid } from '../workers/diagnostics';
import type { SttvDiagnostic } from '../workers/diagnostics';

export function sttvAdaptDatabase(input: unknown, diagnostics: SttvDiagnostic[] = []): SttvCatalog {
  const db = input as SttvDatabase;
  if (db?.format !== config.format || db?.format_version !== config.formatVersion) {
    throw new SttvPreparationError(sttvDiagnostic('unsupported_database', 'preparing', {
      received: { format: typeof db?.format === 'string' ? db.format : null,
        formatVersion: typeof db?.format_version === 'number' ? db.format_version : null },
      supported: { format: config.format, formatVersion: config.formatVersion },
    }));
  }
  if (!Array.isArray(db.documents)) throw sttvInvalid('/documents', 'Cannot enumerate source documents.');
  const technologies: SttvCatalog['technologies'] = Object.create(null);
  const links: SttvCatalog['links'] = [];
  const strings = new SttvIndexBuilder();
  const field = config.fields;

  function area(items: SttvNode[], path: string, inherited?: SttvArea): SttvArea {
    const value = sttvField(items, field.area, path);
    const result = value ? sttvScalar(value, path) : inherited;
    if (!result || !config.areas.includes(result)) throw sttvInvalid(path, 'Research area is missing or unsupported.');
    return result as SttvArea;
  }
  function representation(node: SttvNode, path: string, baseArea: SttvArea, index?: number): SttvRepresentation {
    return { id: index === undefined ? 'base' : `swap:${index}`,
      ...(index === undefined ? {} : { variantNumber: index }),
      area: area(sttvItems(node.value, path), path, baseArea), sourceRef: path,
      ...strings.add(node.enrichments?.localization, path) };
  }
  try {
    db.documents.forEach((document, d) => {
      const file = document.source.file.replaceAll('\\', '/');
      const directory = file.slice(0, file.lastIndexOf('/'));
      if (directory !== config.technologyDirectory || !file.endsWith('.txt')) return;
      document.items.forEach((node, i) => {
        if (node.kind !== 'assignment' || node.value?.kind !== 'block') return;
        const path = `/documents/${d}/items/${i}`;
        const id = sttvScalar(node.key, path);
        if (technologies[id]) throw sttvInvalid(path, `Duplicate technology ID: ${id}`);
        const items = sttvItems(node.value, path);
        const baseArea = area(items, path);
        const tier = Number(sttvScalar(sttvField(items, field.tier, path), path));
        if (!Number.isInteger(tier) || tier < 0) throw sttvInvalid(path, 'Technology tier must be a non-negative integer.');
        const requirementValue = sttvField(items, field.prerequisites, path);
        const requirementIndex = sttvFields(items, field.prerequisites)[0]?.index;
        const requirementPath = requirementIndex === undefined ? path : `${path}/value/items/${requirementIndex}/value`;
        const { links: edges, ...requirements } = sttvRequirements(requirementValue, requirementPath, id);
        const representations = [representation(node, path, baseArea)];
        sttvFields(items, field.variant).forEach(({ node: variant, index }, v) => {
          representations.push(representation(variant, `${path}/value/items/${index}`, baseArea, v + 1));
        });
        technologies[id] = { id, tier, sourceRef: path, representations, ...requirements };
        links.push(...edges);
      });
    });
    for (const link of links) {
      if (!technologies[link.from]) throw sttvInvalid(technologies[link.to].sourceRef,
        `Unresolved technology requirement: ${link.from}`);
    }
    // Every selectable representation must support the same column ordering operation.
    const all = Object.values(technologies);
    for (const tier of new Set(all.map(item => item.tier))) {
      for (const researchArea of config.areas) {
        sttvOrderColumn(all.filter(item => item.tier === tier
          && item.representations.some(view => view.area === researchArea)));
      }
    }
    return { technologies, links, localization: strings.index, diagnostics };
  } finally {
    diagnostics.push(...strings.warnings());
  }
}

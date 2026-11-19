import config from '../../../config/frontend/adapter.json';
import type { SttvNode } from './syntax';
import type { SttvNodeRef } from './model';
import { sttvField, sttvFields, sttvItems, sttvScalar } from './syntax';
import { sttvDiagnostic, sttvInvalid, type SttvDiagnostic } from '../workers/diagnostics';

export function sttvCardValues(items: SttvNode[], path: string, diagnostics: SttvDiagnostic[], context?: { technology: string; sourceRef: SttvNodeRef }) {
  const fields = config.presentation;
  function numeric(key: string, factor = false) {
    try {
      let value = sttvField(items, key, path);
      if (!value) return null;
      if (factor && value.kind === 'block') value = sttvField(sttvItems(value, path), fields.factor, path);
      const raw = sttvScalar(value, path);
      const result = raw.trim() ? Number(raw) : NaN;
      if (!Number.isFinite(result)) throw new Error('Expected a finite base number.');
      return result;
    } catch (error) {
      const index = sttvFields(items, key)[0]?.index;
      diagnostics.push(sttvDiagnostic('card_value_invalid', 'preparing', { ...context, representation: 'base',
        path: index === undefined ? path : `${path}/value/items/${index}/value`, field: key, reason: String(error) }));
      return null;
    }
  }
  function flag(key: string) {
    const values = new Set(sttvFields(items, key).map(({ node }) => sttvScalar(node.value, path).toLowerCase()));
    if (values.size > 1 || [...values].some(value => !['yes', 'no'].includes(value))) {
      throw sttvInvalid(path, `Conflicting or invalid ${key} flag.`);
    }
    return values.has('yes');
  }
  return { cost: numeric(fields.cost, true), weight: numeric(fields.weight),
    rare: flag(fields.rare), dangerous: flag(fields.dangerous) };
}

export function sttvCardRepresentation(node: SttvNode, path: string, inherited: string[] = []) {
  const items = sttvItems(node.value, path);
  const category = sttvFields(items, config.presentation.category);
  const categories = category.length ? category.flatMap(({ node }) =>
    sttvItems(node.value, path).map(item => sttvScalar(item, path))) : inherited;
  return { categories, iconAssetId: node.enrichments?.presentation?.icon_asset_id ?? null };
}

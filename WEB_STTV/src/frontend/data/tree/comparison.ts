import type { SttvRepresentation, SttvCardTechnology } from '../model';
import type { SttvTextRef } from '../../localization/model';
import { sttvTreeError } from './contract';

export type SttvTextLookup = (ref: SttvTextRef) => string;
export function sttvRepresentation(technology: SttvCardTechnology, selected: Record<string, string>): SttvRepresentation {
  const representation = technology.representations.find(item => item.id === selected[technology.id]);
  if (!representation) sttvTreeError('tree_enrichment_invalid', 'Selected representation is missing.', { sourceRef: technology.sourceRef });
  return representation;
}
export function sttvTechnologyName(technology: SttvCardTechnology, representation: SttvRepresentation, text: SttvTextLookup): SttvTextRef {
  const name = { source: 'database' as const, id: representation.nameId };
  const title = text(name);
  const duplicate = technology.representations.filter(item => text({ source: 'database', id: item.nameId }) === title).length > 1;
  return { ...name, ...(duplicate && representation.variantNumber !== undefined
    ? { suffix: { id: 'sttv_variant_suffix', params: { number: representation.variantNumber } } } : {}) };
}

import type { SttvRepresentation, SttvTechnology } from '../model';
import type { SttvLanguage, SttvTextRef } from '../../localization/model';
import type { SttvTreeSettings } from './model';
import { sttvTreeError } from './contract';

export type SttvTextLookup = (ref: SttvTextRef) => string;
export function sttvRepresentation(technology: SttvTechnology, selected: Record<string, string>): SttvRepresentation {
  const representation = technology.representations.find(item => item.id === selected[technology.id]);
  if (!representation) sttvTreeError('tree_enrichment_invalid', 'Selected representation is missing.', { sourceRef: technology.sourceRef });
  return representation;
}
export function sttvTechnologyName(technology: SttvTechnology, representation: SttvRepresentation, text: SttvTextLookup): SttvTextRef {
  const name = { source: 'database' as const, id: representation.nameId };
  const title = text(name);
  const duplicate = technology.representations.filter(item => text({ source: 'database', id: item.nameId }) === title).length > 1;
  return { ...name, ...(duplicate && representation.variantNumber !== undefined
    ? { suffix: { id: 'sttv_variant_suffix', params: { number: representation.variantNumber } } } : {}) };
}
export function sttvTreeComparators(technologies: Record<string, SttvTechnology>, selected: Record<string, string>,
  language: SttvLanguage, settings: SttvTreeSettings, text: SttvTextLookup) {
  const titles = new Map(Object.values(technologies).map(tech =>
    [tech.id, text(sttvTechnologyName(tech, sttvRepresentation(tech, selected), text))]));
  const collator = new Intl.Collator(settings.sort_locales[language]);
  const name = (a: string, b: string) => collator.compare(titles.get(a)!, titles.get(b)!) || (a < b ? -1 : a > b ? 1 : 0);
  const normalized = (id: string) => [...id].filter(char => !settings.ignored_id_characters.includes(char)).join('');
  return {
    roots: (a: string, b: string) => (settings.starting_roots_first
      ? Number(technologies[b].startTech) - Number(technologies[a].startTech) : 0) || name(a, b),
    children: (parent: string) => (a: string, b: string) =>
      Number(normalized(b) === normalized(parent)) - Number(normalized(a) === normalized(parent)) || name(a, b),
  };
}

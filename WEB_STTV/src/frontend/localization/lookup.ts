import config from '../../../config/frontend/localization.json';
import type { SttvLanguage, SttvLocalizedRecord, SttvTextRef } from './model';

export type SttvSources = Record<string, Record<string, Record<string, SttvLocalizedRecord>>>;
export function sttvSource(reader: string, input: unknown, path: string[]) {
  let data = input;
  for (const part of path) data = (data as Record<string, unknown> | undefined)?.[part];
  if (!data) return {};
  if (reader === 'records') return data as SttvSources[string];
  if (reader !== 'strings') throw new Error(`Unsupported localization reader: ${reader}`);
  return Object.fromEntries(Object.entries(data as Record<string, Record<string, string>>)
    .map(([language, strings]) => [language, Object.fromEntries(Object.entries(strings).map(([id, text]) =>
      [id, { status: 'resolved' as const, text, origins: [] }]))]));
}
export function sttvLookup(sources: SttvSources, language: SttvLanguage, ref: SttvTextRef): string {
  const source = ref.source ?? config.defaultSource;
  const record = sources[source]?.[language]?.[ref.id];
  let text = record?.status === 'resolved' && record.text !== null ? record.text : `⟦${ref.id}⟧`;
  if (source === 'builtin' && ref.params) {
    text = text.replace(/\{([A-Za-z_][A-Za-z_0-9]*)\}/g, (token, key: string) =>
      Object.hasOwn(ref.params!, key) ? String(ref.params![key]) : token);
  }
  return text + (ref.suffix ? sttvLookup(sources, language, ref.suffix) : '');
}

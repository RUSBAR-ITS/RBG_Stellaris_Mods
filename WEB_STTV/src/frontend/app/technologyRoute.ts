import type { SttvLanguage } from '../localization/model';

export function technologyLink(id: string, language: SttvLanguage, enabled?: string[]) {
  const params = new URLSearchParams({ lang: language });
  if (enabled) params.set('dlc', [...enabled].sort().join(','));
  return '#/technology/' + encodeURIComponent(id) + '?' + params;
}

export function technologyRoute(hash: string): { id: string; language?: SttvLanguage; enabled?: string[] } | null {
  const match = /^#\/technology\/([^?]+)(?:\?(.*))?$/.exec(hash);
  if (!match) return null;
  const params = new URLSearchParams(match[2]);
  let id = match[1];
  try { id = decodeURIComponent(id); } catch { /* The server handles unknown IDs. */ }
  const lang = params.get('lang');
  return { id, language: lang === 'ru' || lang === 'en' ? lang : undefined,
    enabled: params.has('dlc') ? params.get('dlc')!.split(',').filter(Boolean) : undefined };
}

import { createContext, useContext, useMemo, type ReactNode } from 'react';
import config from '../../../config/frontend/localization.json';
import ru from '../locales/ru.json';
import en from '../locales/en.json';
import { sttvLookup, sttvSource, type SttvSources } from './lookup';
import type { SttvCatalog } from '../data/model';
import type { SttvLanguage, SttvTextRef } from './model';

const sttvBuiltin = sttvSource(config.sources.builtin.reader, { ru, en }, config.sources.builtin.path);
const SttvLocalization = createContext({ language: 'ru' as SttvLanguage,
  text: (ref: SttvTextRef) => `⟦${ref.id}⟧` });
export function SttvLocalizationProvider({ language, data, children }:
  { language: SttvLanguage; data: SttvCatalog | null; children: ReactNode }) {
  const sources = useMemo<SttvSources>(() => ({ builtin: sttvBuiltin,
    database: sttvSource(config.sources.database.reader, data, config.sources.database.path) }), [data]);
  const value = useMemo(() => ({ language, text: (ref: SttvTextRef) => sttvLookup(sources, language, ref) }), [language, sources]);
  return <SttvLocalization.Provider value={value}>{children}</SttvLocalization.Provider>;
}
export function sttvUseLocalization() { return useContext(SttvLocalization); }

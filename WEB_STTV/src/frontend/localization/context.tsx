import { createContext, useContext, useMemo, type ReactNode } from 'react';
import { sttvCreateTextLookup } from './sources';
import type { SttvCatalog } from '../data/model';
import type { SttvLanguage, SttvTextRef } from './model';

const SttvLocalization = createContext({ language: 'ru' as SttvLanguage,
  text: (ref: SttvTextRef) => `⟦${ref.id}⟧` });
export function SttvLocalizationProvider({ language, data, children }:
  { language: SttvLanguage; data: SttvCatalog | null; children: ReactNode }) {
  const value = useMemo(() => ({ language, text: sttvCreateTextLookup(data, language) }), [language, data]);
  return <SttvLocalization.Provider value={value}>{children}</SttvLocalization.Provider>;
}
export function sttvUseLocalization() { return useContext(SttvLocalization); }

import { createContext } from 'react';
import type { SttvLanguage } from '../localization/model';

export interface Expression {
  kind: string;
  key?: string;
  text?: string;
  children?: Expression[];
  formula?: Expression[];
  expression?: unknown;
  evidence?: unknown;
  summary?: string[];
  technology_link?: string;
  source?: string[];
  operations?: Expression[];
  condition?: Expression;
}
export type Sections = Partial<Record<'prerequisites' | 'potential' | 'allow' | 'starting_potential' | 'weight_modifier' | 'weight_notes' | 'research_options' | 'researched_grants' | 'research_progress', Expression[]>>;
export interface TechnologyResponse { technology_id: string; language: SttvLanguage; name: string; description: string; sections: Sections }
class TooltipCache extends Map<string, TechnologyResponse> {
  generation = 0;

  override clear() {
    super.clear();
    this.generation++;
  }
}

export function createTooltipCache() {
  return new TooltipCache();
}
export const TreeTooltipContext = createContext<{
  enabled?: string[]; active: boolean; cache: ReturnType<typeof createTooltipCache>;
}>({ active: true, cache: createTooltipCache() });

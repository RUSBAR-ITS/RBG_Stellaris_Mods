import type { SttvArea, SttvDatabaseKind } from '../model';
import type settings from '../../../../config/frontend/tree_layout.json';
import type { SttvLanguage } from '../../localization/model';
import type { SttvDiagnostic } from '../../workers/diagnostics';
import type { SttvAreaConnections, SttvConnectionSummary } from '../connections/model';

export type SttvTreeSettings = typeof settings;
export interface SttvTreeRecord {
  parent_tech: string | null;
  children: string[];
  status: 'root' | 'resolved' | 'ambiguous';
  visibility?: { visible: boolean; reasons: { code: string; pointer: string }[] };
}
export interface SttvTreeCombination {
  id: string;
  mode: string;
  parameters: { mode: string; profile: Record<string, unknown>; variants: Record<string, string>;
    dlc?: { known: string[]; enabled: string[]; catalog_revision: string } };
  source_set_id: string;
  inputs: { kind: SttvDatabaseKind; algorithm: string; hash: string }[];
  implementation_revision: string;
  input_revision: string;
  rules_revision: string;
  parameters_revision: string;
  calculation_revision: string;
  result_revision: string;
}
export interface SttvPlacement { id: string; column: number; row: number }
export interface SttvAreaLayout {
  area: SttvArea;
  roots: string[];
  cards: SttvPlacement[];
  rowCount: number;
  height: number;
  geometry: SttvAreaConnections;
}
export interface SttvLayoutReport {
  combination: SttvTreeCombination;
  language: SttvLanguage;
  settings: SttvTreeSettings;
  areas: { area: SttvArea; technologies: number; trees: number; rows: number }[];
  hiddenCrossAreaLinks: number;
  columns: number;
  width: number;
  height: number;
  seconds: number;
  connections: SttvConnectionSummary;
}
export interface SttvLayout {
  areas: SttvAreaLayout[];
  tiers: number[];
  columns: number[];
  width: number;
  height: number;
  report: SttvLayoutReport;
  diagnostics: SttvDiagnostic[];
}

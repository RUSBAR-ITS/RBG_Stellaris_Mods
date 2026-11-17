import type { SttvLocalizationIndex } from '../localization/model';
import type { SttvDiagnostic } from '../workers/diagnostics';

export type SttvArea = 'physics' | 'society' | 'engineering';
export type SttvOperator = 'AND' | 'OR' | 'NOT' | 'NAND' | 'NOR';
export type SttvRequirement = { kind: 'technology'; technologyId: string } | SttvGroup;
export interface SttvGroup { kind: 'group'; operator: SttvOperator; items: SttvRequirement[] }
export interface SttvRepresentation {
  id: string;
  variantNumber?: number;
  area: SttvArea;
  nameId: string;
  descriptionId: string;
  sourceRef: string;
}
export interface SttvTechnology {
  id: string;
  tier: number;
  prerequisites: SttvGroup;
  prerequisiteIds: string[];
  requirementCount: number;
  representations: SttvRepresentation[];
  sourceRef: string;
}
export interface SttvLink { from: string; to: string; requirementPaths: number[][] }
export interface SttvCatalog {
  technologies: Record<string, SttvTechnology>;
  links: SttvLink[];
  localization: SttvLocalizationIndex;
  diagnostics: SttvDiagnostic[];
}

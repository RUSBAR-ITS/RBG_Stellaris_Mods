import type { SttvLocalizationIndex } from '../localization/model';
import type { SttvDiagnostic } from '../workers/diagnostics';

export type SttvArea = 'physics' | 'society' | 'engineering';
import type { SttvDatabaseKind } from './registry';
export type { SttvDatabaseKind } from './registry';
export interface SttvNodeRef { database: SttvDatabaseKind; pointer: string }
export interface SttvObjectRef { database: SttvDatabaseKind; id: string }
export type SttvOperator = 'AND' | 'OR' | 'NOT' | 'NAND' | 'NOR';
export type SttvRequirement = { kind: 'technology'; technologyId: string } | SttvGroup;
export interface SttvGroup { kind: 'group'; operator: SttvOperator; items: SttvRequirement[] }
export interface SttvRepresentation {
  id: string;
  variantNumber?: number;
  area: SttvArea;
  nameId: string;
  descriptionId: string;
  sourceRef: SttvNodeRef;
}
export interface SttvTechnology {
  id: string;
  tier: number;
  prerequisites: SttvGroup;
  prerequisiteIds: string[];
  requirementCount: number;
  representations: SttvRepresentation[];
  sourceRef: SttvNodeRef;
}
export interface SttvLink { from: string; to: string; requirementPaths: number[][] }
export interface SttvTechnologyCatalog {
  technologies: Record<string, SttvTechnology>;
  links: SttvLink[];
  localization: SttvLocalizationIndex;
  diagnostics: SttvDiagnostic[];
}
export interface SttvObject {
  id: string;
  templateType?: string;
  nameId: string;
  descriptionId: string;
  sourceRef: SttvNodeRef;
  prerequisites: SttvGroup;
  prerequisitesRef: SttvNodeRef | null;
  conditionalDescriptions: { sourceRef: SttvNodeRef; descriptionId: string; triggerRef: SttvNodeRef | null }[];
}
export interface SttvObjectRequirement {
  from: SttvObjectRef;
  to: SttvObjectRef;
  requirementPaths: number[][];
  sourceRef: SttvNodeRef;
}
export interface SttvObjectUpgrade { from: SttvObjectRef; to: SttvObjectRef; sourceRef: SttvNodeRef }
export interface SttvObjectCatalog {
  objects: Record<string, SttvObject>;
  requirements: SttvObjectRequirement[];
  upgrades: SttvObjectUpgrade[];
}
export interface SttvUpgradeWitness {
  upgrade: SttvObjectUpgrade;
  fromPrerequisitesRef: SttvNodeRef;
  toPrerequisitesRef: SttvNodeRef;
}
export interface SttvUpgradeEvidence { from: string; to: string; witnesses: SttvUpgradeWitness[] }
export interface SttvDatasetInfo {
  kind: SttvDatabaseKind;
  fileIndex: number;
  name: string;
  size: number;
  documentCount: number;
}
export interface SttvCatalog extends SttvTechnologyCatalog {
  setId: string;
  datasets: SttvDatasetInfo[];
  components: Record<string, SttvObject>;
  buildings: Record<string, SttvObject>;
  objectRequirements: SttvObjectRequirement[];
  objectUpgrades: SttvObjectUpgrade[];
  upgradeEvidence: SttvUpgradeEvidence[];
  definitions: Partial<Record<SttvDatabaseKind, SttvDefinition[]>>;
  definitionIndex: Partial<Record<SttvDatabaseKind, Record<string, SttvNodeRef[]>>>;
}

export interface SttvDefinitionText {
  sourceRef: SttvNodeRef;
  nameId?: string;
  descriptionId?: string;
}
export interface SttvDefinition {
  sourceRef: SttvNodeRef;
  type: string;
  id?: string;
  texts: SttvDefinitionText[];
  endpoints?: Record<string, { id: string; sourceRef: SttvNodeRef }>;
}

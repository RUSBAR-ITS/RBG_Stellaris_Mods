import registry from '../../../config/datasets.json' with { type: 'json' };

export type SttvDatabaseKind = keyof typeof registry.datasets;
export interface SttvDatasetSpec {
  labelId: string; directory: string; recursive: boolean; rootTypes: string[];
  identity: string; idField: string | null; containers?: string[];
  sourceRoles?: { role: string; pattern: string }[];
  descriptorLink?: { matchField: string; localizationField: string };
}
export const sttvDatasets: Record<SttvDatabaseKind, SttvDatasetSpec> = registry.datasets;
export const sttvDatabaseKinds = Object.keys(sttvDatasets) as SttvDatabaseKind[];

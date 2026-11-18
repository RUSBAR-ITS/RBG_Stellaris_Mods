import registry from '../../../config/datasets.json' with { type: 'json' };

export const sttvDatasets = registry.datasets;
export type SttvDatabaseKind = keyof typeof sttvDatasets;
export const sttvDatabaseKinds = Object.keys(sttvDatasets) as SttvDatabaseKind[];

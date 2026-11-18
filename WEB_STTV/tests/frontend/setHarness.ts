import { readFileSync } from 'node:fs';
import { sttvDatabaseKinds } from '../../src/frontend/data/registry';
import { sttvAdaptSet as adaptSet } from '../../src/frontend/data/setAdapter';
import type { SttvTargetRegistry } from '../../src/frontend/data/textTargets';

export const sttvRules: SttvTargetRegistry = Object.fromEntries(sttvDatabaseKinds.map(kind =>
  [kind, JSON.parse(readFileSync(`config/enrichment/targets/${kind}.json`, 'utf8'))]));
export const sttvAdaptSet = (inputs: unknown[], files: { name: string; size: number }[]) => adaptSet(inputs, files, sttvRules);

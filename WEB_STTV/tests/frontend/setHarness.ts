import { readFileSync } from 'node:fs';
import { sttvDatabaseKinds } from '../../src/frontend/data/registry';
import { SttvSetAdapter } from '../../src/frontend/data/setAdapter';
import { sttvCheckManifest } from '../../src/frontend/storage/manifest';
import type { SttvDatabase } from '../../src/frontend/data/syntax';
import { sttvBundle } from './manifestFixtures';
import { sttvSetError } from '../../src/frontend/data/setMetadata';
import type { SttvTargetRegistry } from '../../src/frontend/data/textTargets';

export const sttvRules: SttvTargetRegistry = Object.fromEntries(sttvDatabaseKinds.map(kind =>
  [kind, JSON.parse(readFileSync(`config/enrichment/targets/${kind}.json`, 'utf8'))]));
export function sttvAdaptSet(inputs: SttvDatabase[], _files: { name: string; size: number }[] = []) {
  if (inputs.length !== sttvDatabaseKinds.length || new Set(inputs.map(d => d.database)).size !== sttvDatabaseKinds.length
    || inputs.some(d => d.format !== 'sttv.parse_document' || d.format_version !== 1)) sttvSetError('Invalid fixture set.');
  const { manifest } = sttvBundle(inputs);
  sttvCheckManifest(manifest);
  const adapter = new SttvSetAdapter(manifest, sttvRules);
  for (const kind of sttvDatabaseKinds) for (const db of inputs.filter(d => d.database === kind)) {
    adapter.document(db, 0); adapter.completed(kind, db.document_id);
  }
  return adapter.finish({ declaredDocuments: inputs.length, verifiedDocuments: inputs.length,
    notCheckedDocuments: 0, bytesRead: 0, seconds: 0, documents: [] });
}

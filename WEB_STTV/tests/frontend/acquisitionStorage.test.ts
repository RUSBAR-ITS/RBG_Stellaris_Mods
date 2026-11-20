import test from 'node:test';
import assert from 'node:assert/strict';
import { SttvStorageSession } from '../../src/frontend/storage/session';
import { sttvBundle } from './manifestFixtures';
import { sttvSet } from './fixtures';
import { sttvRules } from './setHarness';

test('opening requires acquisition membership but does not read semantic evidence', async () => {
  const bundle = sttvBundle(sttvSet());
  bundle.manifest.acquisition.documents.push({ path: 'acquisition/example.json', file_hash: 'a'.repeat(64), byte_size: 2 });
  bundle.entries.find(e => e.path === 'manifest.json')!.content = JSON.stringify(bundle.manifest);
  const files = bundle.entries.map(e => {
    const file = new File([e.content], e.path);
    Object.defineProperty(file, 'webkitRelativePath', { value: 'set/' + e.path });
    return file;
  });
  await assert.rejects(SttvStorageSession.open(files, sttvRules));
  const evidence = new File(['{}'], 'example.json');
  Object.defineProperty(evidence, 'webkitRelativePath', { value: 'set/acquisition/example.json' });
  evidence.stream = () => { throw new Error('The frontend must not read acquisition evidence.'); };
  const session = await SttvStorageSession.open([...files, evidence], sttvRules);
  const initial = await session.initial();
  assert.equal(initial.coverage.verifiedDocuments, 1);
  assert.equal(initial.datasets.length, 30);
});

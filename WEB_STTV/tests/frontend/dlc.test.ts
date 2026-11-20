import test from 'node:test';
import assert from 'node:assert/strict';
import { SttvStorageSession } from '../../src/frontend/storage/session';
import { sttvAllDlcCombination } from '../../src/frontend/workers/dlc';
import { sttvBundle, sttvFiles } from './manifestFixtures';
import { sttvRules } from './setHarness';
import { sttvDlcFixture } from './dlcFixture';
import type { SttvTreeCombination } from '../../src/frontend/data/tree/model';
const combos = (manifest: { technology_tree?: unknown }) =>
  (manifest.technology_tree as { combinations: Record<string, SttvTreeCombination> }).combinations;

test('snapshot refresh rereads changed technology bytes, keeps catalogs and rejects corruption atomically', async () => {
  const inputs = sttvDlcFixture(), files = sttvFiles(inputs);
  const session = await SttvStorageSession.open(files, sttvRules);
  const original = await session.initial();
  await session.load(['dlcs']);
  const changed = structuredClone(inputs);
  const nodes = changed.find(d => d.database === 'technologies')!.items;
  Object.assign((nodes[0].enrichments!.technology_tree as any).reference_default,
    { children: [], visibility: { visible: false, reasons: [{ code: 'dlc_potential', pointer: '/value' }] } });
  Object.assign((nodes[1].enrichments!.technology_tree as any).reference_default, { parent_tech: null, status: 'root' });
  const next = sttvBundle(changed);
  next.manifest.snapshot_revision = 'f'.repeat(64);
  combos(next.manifest).reference_default.parameters.dlc!.enabled = [];
  const previous = session.reader.manifest;
  next.manifest.datasets.technologies.documents[0].source_hash = previous.datasets.technologies.documents[0].source_hash;
  const fetched: string[] = [];
  const remote = async (path: string) => {
    fetched.push(path);
    return new Blob([next.entries.find(entry => entry.path === path)!.content]);
  };
  const refreshed = await session.refresh(next.manifest, 'reference_default', remote);
  assert.equal(fetched.length, 1);
  assert.equal(refreshed.data.technologies.parent.tree.visibility!.visible, false);
  assert.equal(refreshed.data.technologies.child.tree.parent_tech, null);
  assert.equal(refreshed.data.definitions.dlcs!.length, 2);
  assert.equal(refreshed.data.coverage.verifiedDocuments, 2);
  assert.equal(original.technologies.child.tree.parent_tech, 'parent');
  await refreshed.session.refresh(next.manifest, 'reference_default', remote);
  assert.equal(fetched.length, 1);
  await assert.rejects(session.refresh(next.manifest, 'reference_default', async () => new Blob(['{}'])));
  assert.equal((await session.initial()).technologies.child.tree.parent_tech, 'parent');
});

test('offline opening selects only an all-enabled profile with the same variants', () => {
  const { manifest } = sttvBundle(sttvDlcFixture());
  assert.equal(sttvAllDlcCombination(manifest), 'reference_default');
  const all = structuredClone(combos(manifest).reference_default);
  all.id = 'all';
  combos(manifest).all = all;
  combos(manifest).reference_default.parameters.dlc!.enabled = [];
  assert.equal(sttvAllDlcCombination(manifest), 'all');
  all.parameters.variants.child = 'swap:1';
  assert.equal(sttvAllDlcCombination(manifest), undefined);
});

import test from 'node:test';
import assert from 'node:assert/strict';
import { SttvStorageSession } from '../../src/frontend/storage/session';
import { sttvCheckManifest } from '../../src/frontend/storage/manifest';
import { sttvSet, sttvAssignment as field, sttvBlock as block, sttvScalar as scalar, sttvLocalization } from './fixtures';
import { sttvFiles, sttvBundle } from './manifestFixtures';
import { sttvRules } from './setHarness';
import { sttvLookup } from '../../src/frontend/localization/lookup';

test('DLC objects use nested addresses and load on request without loading other catalogs', async () => {
  const inputs = sttvSet(), dlc = inputs.find(d => d.database === 'dlcs')!;
  const localized = sttvLocalization('TITLE');
  delete localized.ru.description; delete localized.en.description;
  dlc.items = [field('dlcs', block([{ ...field('dlc036', block([
    field('name', scalar('BioGenesis')), field('localizable_name', scalar('TITLE'))])),
    enrichments: { localization: localized } }]))];
  const files = sttvFiles(inputs), session = await SttvStorageSession.open(files, sttvRules);
  const initial = await session.initial();
  assert.equal(initial.coverage.verifiedDocuments, 1);
  assert.equal(initial.definitions.dlcs, undefined);
  const selected = await session.resolve([{ database: 'dlcs', id: 'dlc036' }]);
  assert.equal(selected.refs[0].pointer, '/items/0/value/items/0');
  assert.equal(selected.data.definitions.dlcs![0].id, 'dlc036');
  assert.equal(selected.data.localization.en.TITLE.text, 'TITLE');
  assert.equal(selected.data.coverage.verifiedDocuments, 2);
  const reused = await session.resolveNodes(selected.refs);
  assert.equal(reused.data.coverage.bytesRead, selected.data.coverage.bytesRead);
  const bundle = sttvBundle(inputs);
  bundle.manifest.datasets.dlcs.objects[0].pointer = '/items/0';
  assert.throws(() => sttvCheckManifest(bundle.manifest));
  assert.throws(() => session.resolveNodes([{ ...selected.refs[0], pointer: '/items/0/value/items/999' }]));
});

test('missing DLC translation uses the technical name without reporting a resolved translation', async () => {
  const inputs = sttvSet(), dlc = inputs.find(d => d.database === 'dlcs')!;
  const localized = sttvLocalization('ABSENT', null);
  delete localized.ru.description; delete localized.en.description;
  dlc.items = [field('dlcs', block([{ ...field('dlc036', block([
    field('name', scalar('BioGenesis')), field('localizable_name', scalar('ABSENT'))])), enrichments: { localization: localized } }]))];
  const session = await SttvStorageSession.open(sttvFiles(inputs), sttvRules);
  const { data } = await session.resolve([{ database: 'dlcs', id: 'dlc036' }]);
  assert.equal(data.localization.en.ABSENT.status, 'missing');
  assert.equal(data.localization.en.ABSENT.text, null);
  assert.equal(sttvLookup({ database: data.localization }, 'en', { source: 'database', id: 'ABSENT' }), 'BioGenesis');
});

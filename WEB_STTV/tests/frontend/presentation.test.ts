import test from 'node:test';
import assert from 'node:assert/strict';
import { sttvCardValues, sttvCardRepresentation } from '../../src/frontend/data/presentation';
import { sttvAssignment as a, sttvScalar as s, sttvBlock as b } from './fixtures';
import { sttvCheckPresentation, sttvLoadAssets } from '../../src/frontend/storage/assets';
import { sttvRelative } from '../../src/frontend/storage/manifest';
import type { SttvDiagnostic } from '../../src/frontend/workers/diagnostics';
import { sttvDatabase, sttvTechnology, sttvSet } from './fixtures';
import { sttvFiles } from './manifestFixtures';
import { SttvStorageSession } from '../../src/frontend/storage/session';
import { sttvRules } from './setHarness';
import { sttvImageFixture } from './imageFixture';
import type { SttvCachedImage } from '../../src/frontend/storage/assets';

test('missing numbers stay absent, explicit zero survives and conditional cost uses only base factor', () => {
  const diagnostics: SttvDiagnostic[] = [];
  assert.deepEqual(sttvCardValues([], '', diagnostics), { cost: null, weight: null, rare: false, dangerous: false });
  const fields = [a('cost', b([a('factor', s('2500')), a('modifier', b([a('factor', s('0.5'))]))])),
    a('weight', s('0')), a('is_rare', s('yes')), a('is_dangerous', s('yes'))];
  assert.deepEqual(sttvCardValues(fields, '/items/1', diagnostics), { cost: 2500, weight: 0, rare: true, dangerous: true });
  assert.equal(diagnostics.length, 0);
  assert.equal(sttvCardValues([a('is_dangerous', s('yes')), a('is_dangerous', s('yes'))], '', diagnostics).dangerous, true);
  assert.throws(() => sttvCardValues([a('is_dangerous', s('yes')), a('is_dangerous', s('no'))], '', diagnostics));
  assert.equal(sttvCardValues([a('weight', s('invalid'))], '/items/2', diagnostics).weight, null);
  assert.equal(diagnostics[0].code, 'card_value_invalid');
});

test('variant category list replaces the entire inherited list and keeps the prepared image identity', () => {
  const node = a('technology_swap', b([a('category', b([s('biology'), s('psionics')]))]));
  node.enrichments = { presentation: { format_version: 1, icon_asset_id: 'a'.repeat(64) } };
  assert.deepEqual(sttvCardRepresentation(node, '', ['computing']), { categories: ['biology', 'psionics'], iconAssetId: 'a'.repeat(64) });
  assert.deepEqual(sttvCardRepresentation(a('swap', b([])), '', ['computing']).categories, ['computing']);
});

test('resource contract rejects path collisions and opening an unprepared set requires explicit preparation', async () => {
  const id = 'a'.repeat(64);
  const value = { format_version: 1 as const, revision: id, categories: {}, research_icons: { physics: id, society: null, engineering: null },
    files: { [id]: { path: '../outside.png', file_hash: id, byte_size: 100, width: 10, height: 10, mime_type: 'image/png' as const } } };
  assert.throws(() => sttvCheckPresentation(value, sttvRelative, new Set()));
  const files = sttvFiles(sttvSet(sttvDatabase([sttvTechnology('x')])));
  const manifest = files.find(file => file.name === 'manifest.json')!;
  const data = JSON.parse(await manifest.text()); delete data.presentation;
  const replaced = new File([JSON.stringify(data)], 'manifest.json');
  Object.defineProperty(replaced, 'webkitRelativePath', { value: manifest.webkitRelativePath });
  await assert.rejects(SttvStorageSession.open(files.map(f => f === manifest ? replaced : f), sttvRules),
    (error: any) => error.diagnostic.code === 'assets_not_prepared');
});

test('one verified image read serves all cards and cached corruption remains in subsequent reports', async () => {
  const fixture = sttvImageFixture();
  const files = fixture.entries.map(entry => {
    const file = new File([entry.content], entry.path.split('/').at(-1)!);
    Object.defineProperty(file, 'webkitRelativePath', { value: `set/${entry.path}` });
    return file;
  });
  const image = files.find(file => file.name.endsWith('.png'))!;
  const stream = image.stream.bind(image); let reads = 0;
  image.stream = () => { reads++; return stream(); };
  const session = await SttvStorageSession.open(files, sttvRules);
  const first = await session.initial();
  assert.equal(reads, 1);
  await session.initial(); assert.equal(reads, 1);
  const cache = new Map<string, SttvCachedImage>();
  for (let i = 0; i < 2; i++) {
    const catalog = { ...first, diagnostics: [] };
    await sttvLoadAssets(catalog, fixture.presentation, new Map(), cache);
    assert.equal(catalog.diagnostics.length, 1);
    assert.equal(catalog.images![fixture.id], null);
  }
});

import test from 'node:test';
import assert from 'node:assert/strict';
import { SttvStorageSession } from '../../src/frontend/storage/session';
import { sttvDatabaseKinds } from '../../src/frontend/data/registry';
import { sttvSet, sttvAssignment as field, sttvBlock as block, sttvLocalization } from './fixtures';
import { sttvFiles, sttvBundle } from './manifestFixtures';
import { sttvRules } from './setHarness';
import { sttvCheckManifest } from '../../src/frontend/storage/manifest';

test('30-kind set opens without eagerly reading ascension catalogs; requested objects retain localized keys', async () => {
  assert.equal(sttvDatabaseKinds.length, 30);
  const inputs = sttvSet();
  for (const kind of ['ascension_perks', 'traditions', 'tradition_categories'] as const) {
    const localization = sttvLocalization(kind + '_example');
    if (kind === 'traditions') for (const language of ['ru', 'en'] as const) {
      Object.assign(localization[language].description!, { key: kind + '_example_delayed',
        requested_key: kind + '_example_delayed' });
    }
    inputs.find(d => d.database === kind)!.items = [{ ...field(kind + '_example', block([])),
      enrichments: { localization } }];
  }
  const session = await SttvStorageSession.open(sttvFiles(inputs), sttvRules);
  assert.equal((await session.initial()).coverage.verifiedDocuments, 1);
  for (const kind of ['ascension_perks', 'traditions', 'tradition_categories'] as const) {
    const loaded = await session.resolve([{ database: kind, id: kind + '_example' }]);
    assert.equal(loaded.refs[0].database, kind);
    assert.equal(loaded.data.definitions[kind]![0].id, kind + '_example');
    assert.ok(loaded.data.localization.ru[kind + '_example']);
    assert.ok(loaded.data.localization.en[kind + '_example']);
  }
  const old = sttvBundle(inputs).manifest;
  delete (old.datasets as Partial<typeof old.datasets>).traditions;
  assert.throws(() => sttvCheckManifest(old), (error: any) =>
    /Prepare a new database set/.test(error.diagnostic.details.reason));
});

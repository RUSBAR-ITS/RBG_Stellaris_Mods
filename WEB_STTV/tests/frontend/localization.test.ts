import test from 'node:test';
import assert from 'node:assert/strict';
import { SttvIndexBuilder } from '../../src/frontend/localization/index';
import { sttvLookup, sttvSource } from '../../src/frontend/localization/lookup';
import { SttvPreparationError } from '../../src/frontend/workers/diagnostics';
import { sttvLocalization } from './fixtures';
import ru from '../../src/frontend/locales/ru.json';
import en from '../../src/frontend/locales/en.json';

test('matching texts merge origins, missing entries can resolve, empty strings are valid', () => {
  const builder = new SttvIndexBuilder();
  builder.add(sttvLocalization('a', null), '/one');
  builder.add(sttvLocalization('a', ''), '/two');
  builder.add(sttvLocalization('a', ''), '/three');
  assert.equal(builder.index.ru.a.text, '');
  assert.equal(builder.index.ru.a.status, 'resolved');
  assert.equal(builder.index.ru.a.origins.length, 3);
  assert.equal(builder.warnings().length, 0);
});
test('inheritance retains requested addresses and all original metadata', () => {
  const loc = sttvLocalization('variant');
  loc.ru.description!.key = 'base_desc';
  loc.ru.description!.inherited_from = 'base';
  const builder = new SttvIndexBuilder();
  builder.add(loc, '/variant');
  assert.equal(builder.index.ru.variant_desc.origins[0].key, 'base_desc');
  assert.deepEqual(builder.index.ru.variant_desc.origins[0].inheritedFrom, { database: 'technologies', pointer: 'base' });
});
test('conflicting resolved texts block preparation with text-specific evidence', () => {
  const builder = new SttvIndexBuilder();
  builder.add(sttvLocalization('a', null), '/missing');
  builder.add(sttvLocalization('a', 'first'), '/first');
  assert.throws(() => builder.add(sttvLocalization('a', 'second'), '/second'), (error: unknown) => {
    assert.ok(error instanceof SttvPreparationError);
    assert.equal(error.diagnostic.code, 'localization_conflict');
    assert.equal(JSON.stringify(error.diagnostic.details).includes('/missing'), false);
    return true;
  });
});
test('lookup uses explicit source, no language fallback, and preserves game text', () => {
  const builder = new SttvIndexBuilder();
  const loc = sttvLocalization('a', 'Raw $key$ [Scope.Name] §G{name}§!');
  loc.ru.name!.text = null;
  builder.add(loc, '/a');
  const sources = { builtin: sttvSource('strings', { en: { count: 'Count {n}' } }, []), database: builder.index };
  assert.equal(sttvLookup(sources, 'ru', { id: 'a', source: 'database' }), '⟦a⟧');
  assert.equal(sttvLookup(sources, 'en', { id: 'a', source: 'database', params: { name: 'changed' } }),
    'Raw $key$ [Scope.Name] §G{name}§!');
  assert.equal(sttvLookup(sources, 'en', { id: 'count', params: { n: 7 } }), 'Count 7');
  assert.equal(builder.warnings().length, 1);
});
test('interface dictionaries have identical keys and parameter names', () => {
  assert.deepEqual(Object.keys(ru).sort(), Object.keys(en).sort());
  for (const id of Object.keys(ru) as (keyof typeof ru)[]) {
    assert.deepEqual(ru[id].match(/\{\w+\}/g), en[id].match(/\{\w+\}/g));
  }
});

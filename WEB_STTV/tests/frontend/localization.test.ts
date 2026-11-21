import test from 'node:test';
import assert from 'node:assert/strict';
import { sttvLookup, sttvSource } from '../../src/frontend/localization/lookup';
import ru from '../../src/frontend/locales/ru.json';
import en from '../../src/frontend/locales/en.json';

test('lookup preserves raw game text, empty strings and source language', () => {
  const game = 'Raw $key$ [Scope.Name] §G{name}§!';
  const sources = { builtin: sttvSource('strings', { en: { count: 'Count {n}' } }, []),
    database: sttvSource('strings', { en: { a: game, empty: '' } }, []) };
  assert.equal(sttvLookup(sources, 'ru', { id: 'a', source: 'database' }), '⟦a⟧');
  assert.equal(sttvLookup(sources, 'en', { id: 'a', source: 'database', params: { name: 'changed' } }), game);
  assert.equal(sttvLookup(sources, 'en', { id: 'empty', source: 'database' }), '');
  assert.equal(sttvLookup(sources, 'en', { id: 'count', params: { n: 7 } }), 'Count 7');
});
test('interface dictionaries have identical keys and parameter names', () => {
  assert.deepEqual(Object.keys(ru).sort(), Object.keys(en).sort());
  for (const id of Object.keys(ru) as (keyof typeof ru)[]) {
    assert.deepEqual(ru[id].match(/\{\w+\}/g), en[id].match(/\{\w+\}/g));
  }
});

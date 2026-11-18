import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { sttvAdaptDatabase } from '../../src/frontend/data/adapter';
import { sttvLayout } from '../../src/frontend/data/layout';
import { SttvPreparationError } from '../../src/frontend/workers/diagnostics';
import { sttvDatabase, sttvTechnology, sttvVariant, sttvScalar, sttvLogical } from './fixtures';

test('requirements preserve groups, repeated paths, and count alternatives once', () => {
  const db = sttvDatabase([sttvTechnology('a'), sttvTechnology('b'), sttvTechnology('c', 0, 'physics', [
    sttvScalar('a'), sttvLogical('OR', [sttvScalar('a'), sttvScalar('b')]),
  ])]);
  const catalog = sttvAdaptDatabase(db);
  assert.equal(catalog.technologies.c.requirementCount, 2);
  assert.deepEqual(catalog.technologies.c.prerequisiteIds, ['a', 'b']);
  assert.deepEqual(catalog.links, [
    { from: 'a', to: 'c', requirementPaths: [[0], [1, 0]] },
    { from: 'b', to: 'c', requirementPaths: [[1, 1]] },
  ]);
  assert.deepEqual(sttvLayout(catalog.technologies, {}).areas[0].columns[0].ids, ['a', 'b', 'c']);
});
test('variants inherit the tier and requirements while selecting their area', () => {
  const base = sttvTechnology('a', 2);
  base.value!.items!.push(sttvVariant('a', 'society'), sttvVariant('b'));
  const catalog = sttvAdaptDatabase(sttvDatabase([base]));
  assert.deepEqual(catalog.technologies.a.representations.map(view => [view.id, view.area]),
    [['base', 'physics'], ['swap:1', 'society'], ['swap:2', 'physics']]);
  const layout = sttvLayout(catalog.technologies, { a: 'swap:1' });
  assert.deepEqual(layout.areas[1].columns[2].ids, ['a']);
  assert.deepEqual(layout.areas[0].columns[2].ids, []);
});
test('category subdirectories and unrelated commands are not treated as technologies', () => {
  const db = sttvDatabase([sttvTechnology('a')]);
  db.documents.push({ source: { file: 'common/technology/category/test.txt', root: 'STELLARIS_ROOT' }, items: [sttvTechnology('ignore')] });
  assert.deepEqual(Object.keys(sttvAdaptDatabase(db).technologies), ['a']);
});
test('unusable requirements produce an explicit preparation error', () => {
  for (const items of [
    [sttvTechnology('a', 0, 'physics', [sttvScalar('missing')])],
    [sttvTechnology('a'), sttvTechnology('a')],
    [sttvTechnology('a', 0, 'physics', [sttvScalar('b')]), sttvTechnology('b', 0, 'physics', [sttvScalar('a')])],
    [sttvTechnology('a', 0, 'physics', [sttvLogical('OR', [sttvLogical('NOT', [sttvScalar('a')])])])],
  ]) assert.throws(() => sttvAdaptDatabase(sttvDatabase(items)), SttvPreparationError);
});
test('layout orders by requirement count then predecessor set and stable ID', () => {
  const items = [sttvTechnology('z'), sttvTechnology('a'),
    sttvTechnology('c', 1, 'physics', [sttvScalar('a')]),
    sttvTechnology('b', 1, 'physics', [sttvScalar('z')]),
    sttvTechnology('d', 1, 'physics', [sttvScalar('a')])];
  const catalog = sttvAdaptDatabase(sttvDatabase(items));
  assert.deepEqual(sttvLayout(catalog.technologies, {}).areas[0].columns[1].ids, ['c', 'd', 'b']);
});
test('real technology set member database produces the agreed catalog without input mutation', { skip: !process.env.STTV_DATABASE_DIR }, () => {
  const db = JSON.parse(readFileSync(`${process.env.STTV_DATABASE_DIR ?? 'data/databases'}/technologies.json`, 'utf8'));
  const catalog = sttvAdaptDatabase(db);
  assert.equal(Object.keys(catalog.technologies).length, 679);
  assert.equal(Object.values(catalog.technologies).reduce((n, t) => n + t.representations.length - 1, 0), 206);
  assert.equal(catalog.technologies.tech_titans.requirementCount, 1);
  assert.deepEqual(catalog.technologies.tech_titans.prerequisiteIds, ['tech_battleships', 'tech_stinger_growth_2']);
  assert.deepEqual(catalog.technologies.tech_titans.sourceRef, { database: 'technologies', pointer: '/documents/7/items/5' });
  assert.equal(catalog.diagnostics.length, 0);
  const serialized = JSON.stringify(catalog);
  assert.equal(serialized.includes('"documents"'), false);
  assert.equal(db.documents[7].items[5].key.text, 'tech_titans');
  console.log(JSON.stringify({ technologies: 679, variants: 206, links: catalog.links.length,
    strings: Object.keys(catalog.localization.ru).length + Object.keys(catalog.localization.en).length,
    mainThreadBytes: Buffer.byteLength(serialized) }));
});

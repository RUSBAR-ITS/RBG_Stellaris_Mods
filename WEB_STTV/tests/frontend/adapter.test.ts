import test from 'node:test';
import assert from 'node:assert/strict';
import { SttvStorageSession } from '../../src/frontend/storage/session';
import { sttvRealFiles } from './realFiles';
import { sttvRules } from './setHarness';
import { sttvAdaptDatabase } from '../../src/frontend/data/adapter';
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
});
test('variants inherit the tier and requirements while selecting their area', () => {
  const base = sttvTechnology('a', 2);
  base.value!.items!.push(sttvVariant('a', 'society'), sttvVariant('b'));
  const catalog = sttvAdaptDatabase(sttvDatabase([base]));
  assert.deepEqual(catalog.technologies.a.representations.map(view => [view.id, view.area]),
    [['base', 'physics'], ['swap:1', 'society'], ['swap:2', 'physics']]);
});
test('category subdirectories and unrelated commands are not treated as technologies', () => {
  const db = sttvDatabase([sttvTechnology('a')]);
  assert.deepEqual(Object.keys(sttvAdaptDatabase(db).technologies), ['a']);
  db.source.file = 'common/technology/category/test.txt';
  assert.deepEqual(Object.keys(sttvAdaptDatabase(db).technologies), []);
});
test('unusable requirements produce an explicit preparation error', () => {
  for (const items of [
    [sttvTechnology('a', 0, 'physics', [sttvScalar('missing')])],
    [sttvTechnology('a'), sttvTechnology('a')],
    [sttvTechnology('a', 0, 'physics', [sttvLogical('OR', [sttvLogical('NOT', [sttvScalar('a')])])])],
  ]) assert.throws(() => sttvAdaptDatabase(sttvDatabase(items)), SttvPreparationError);
});
test('starting and repeatable fields are extracted from the base definition with explicit defaults', () => {
  const node = sttvTechnology('a', 5);
  node.value!.items!.push({ kind: 'assignment', key: sttvScalar('start_tech'), value: sttvScalar('yes') },
    { kind: 'assignment', key: sttvScalar('levels'), value: sttvScalar('-1') });
  const { technologies } = sttvAdaptDatabase(sttvDatabase([node, sttvTechnology('b')]));
  assert.equal(technologies.a.startTech, true); assert.equal(technologies.a.levels, -1);
  assert.equal(technologies.b.startTech, false); assert.equal(technologies.b.levels, null);
  node.value!.items!.push({ kind: 'assignment', key: sttvScalar('start_tech'), value: sttvScalar('yes') });
  assert.equal(sttvAdaptDatabase(sttvDatabase([node])).technologies.a.startTech, true);
  node.value!.items!.push({ kind: 'assignment', key: sttvScalar('start_tech'), value: sttvScalar('no') });
  assert.throws(() => sttvAdaptDatabase(sttvDatabase([node])), SttvPreparationError);
});
test('real technology set member database produces the agreed catalog without input mutation', { skip: !process.env.STTV_DATABASE_DIR }, async () => {
  const session = await SttvStorageSession.open(await sttvRealFiles(process.env.STTV_DATABASE_DIR!), sttvRules);
  const catalog = await session.initial();
  assert.equal(Object.keys(catalog.technologies).length, 679);
  assert.equal(Object.values(catalog.technologies).reduce((n, t) => n + t.representations.length - 1, 0), 206);
  assert.equal(catalog.technologies.tech_titans.requirementCount, 1);
  assert.deepEqual(catalog.technologies.tech_titans.prerequisiteIds, ['tech_battleships', 'tech_stinger_growth_2']);
  assert.match(catalog.technologies.tech_titans.sourceRef.document_id, /^[a-f0-9]{64}$/);
  assert.equal(catalog.technologies.tech_titans.sourceRef.pointer, '/items/5');
  assert.deepEqual(catalog.diagnostics.map(d => ({ code: d.code, technology: d.details.technology,
    field: d.details.field })).sort((a, b) => String(a.technology).localeCompare(String(b.technology))), [
    { code: 'card_value_invalid', technology: 'tech_dyson_gun', field: 'weight' },
    { code: 'card_value_invalid', technology: 'tech_dyson_swarm', field: 'weight' },
    { code: 'card_value_invalid', technology: 'tech_orbital_arc_furnace', field: 'weight' },
  ]);
  const serialized = JSON.stringify(catalog);
  assert.equal(serialized.includes('"kind":"assignment"'), false);
  console.log(JSON.stringify({ technologies: 679, variants: 206, links: catalog.links.length,
    strings: Object.keys(catalog.localization.ru).length + Object.keys(catalog.localization.en).length,
    mainThreadBytes: Buffer.byteLength(serialized) }));
});

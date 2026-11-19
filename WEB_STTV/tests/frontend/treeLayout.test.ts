import test from 'node:test';
import assert from 'node:assert/strict';
import { sttvAdaptDatabase } from '../../src/frontend/data/adapter';
import { sttvLayout } from '../../src/frontend/data/tree/layout';
import { sttvValidateTree } from '../../src/frontend/data/tree/validation';
import { sttvTechnologyName, sttvRepresentation } from '../../src/frontend/data/tree/comparison';
import { sttvCreateTextLookup } from '../../src/frontend/localization/sources';
import type { SttvNode } from '../../src/frontend/data/syntax';
import { sttvDatabase, sttvTechnology as tech, sttvVariant } from './fixtures';
import { sttvCombination, sttvConnect } from './treeFixtures';

function catalog(nodes: SttvNode[], parents: Record<string, string | null> = {}) {
  sttvConnect(nodes, parents);
  const data = { ...sttvAdaptDatabase(sttvDatabase(nodes)), treeCombination: sttvCombination(nodes.map(node => node.key!.text!)) };
  sttvValidateTree(data.technologies, data.treeCombination);
  return data;
}
const positions = (layout: ReturnType<typeof sttvLayout>) => Object.fromEntries(layout.areas.flatMap(area =>
  area.cards.map(card => [card.id, [area.area, card.column, card.row]])));

test('approved fork keeps its continuation and all branch gaps', () => {
  const data = catalog([tech('A1', 1), tech('A2', 1), tech('A3', 2), tech('A4', 3), tech('B1', 2), tech('B2', 3)],
    { A2: 'A1', A3: 'A2', A4: 'A3', B1: 'A1', B2: 'B1' });
  assert.deepEqual(positions(sttvLayout(data, 'en')), {
    A1: ['physics', 1, 0], A2: ['physics', 1, 1], A3: ['physics', 2, 1], A4: ['physics', 3, 1],
    B1: ['physics', 2, 2], B2: ['physics', 3, 2],
  });
});

test('3 -> 4 -> 3 moves the colliding descendant, not its intermediate parent', () => {
  const data = catalog([tech('A', 3), tech('B', 4), tech('C', 3), tech('D', 0)], { B: 'A', C: 'B', D: 'C' });
  assert.deepEqual(positions(sttvLayout(data, 'en')), {
    A: ['physics', 3, 0], B: ['physics', 4, 0], C: ['physics', 3, 1], D: ['physics', 0, 1],
  });
});

test('nested forks reserve complete subtrees and whole roots do not fill their holes', () => {
  const data = catalog([tech('A1', 0), tech('A2', 4), tech('A3', 4), tech('A4', 0),
    tech('B', 2), tech('C', 1), tech('Z', 0)], { A2: 'A1', A3: 'A2', A4: 'A3', B: 'A2', C: 'A1' });
  const layout = sttvLayout(data, 'en');
  assert.deepEqual(positions(layout), { A1: ['physics', 0, 0], A2: ['physics', 4, 0],
    A3: ['physics', 4, 1], A4: ['physics', 0, 1], B: ['physics', 2, 2], C: ['physics', 1, 3], Z: ['physics', 0, 4] });
  assert.equal(layout.areas[0].rowCount, 5);
});

test('starting priority applies only to local roots, not to starting descendants', () => {
  const data = catalog([tech('A'), tech('B'), tech('Z'), tech('child')], { child: 'B' });
  data.technologies.Z.startTech = true; data.technologies.child.startTech = true;
  const layout = sttvLayout(data, 'en');
  assert.deepEqual(layout.areas[0].roots, ['Z', 'A', 'B']);
  assert.deepEqual(layout.areas[0].cards.map(card => card.id), ['Z', 'A', 'B', 'child']);
});

test('cross-area children and returning descendants become local roots without changing saved links', () => {
  const data = catalog([tech('A', 2), tech('B', 1, 'society'), tech('C', 0), tech('D', 1)], { B: 'A', C: 'B', D: 'C' });
  const before = JSON.stringify(data);
  const layout = sttvLayout(data, 'ru');
  assert.deepEqual(layout.areas[0].roots, ['A', 'C']); assert.deepEqual(layout.areas[1].roots, ['B']);
  assert.equal(layout.report.hiddenCrossAreaLinks, 2);
  assert.equal(JSON.stringify(data), before);
});

test('repeatable display level requires tier 5 and a technology prerequisite in any area', () => {
  const data = catalog([tech('a', 5), tech('b', 5), tech('c', 4), tech('d', 5), tech('p', 2, 'society')]);
  for (const id of ['a', 'b', 'c']) data.technologies[id].levels = -1;
  for (const id of ['a', 'c', 'd']) data.technologies[id].prerequisiteIds = ['p'];
  const layout = sttvLayout(data, 'ru'), pos = positions(layout);
  assert.equal(pos.a[1], 6); assert.equal(pos.b[1], 5); assert.equal(pos.c[1], 4); assert.equal(pos.d[1], 5);
  assert.equal(data.technologies.a.tier, 5); assert.equal(layout.tiers.length, 7);
});

test('language, stable ties and multiple normalized ID matches determine order reproducibly', () => {
  const data = catalog([tech('chain1'), tech('chain2', 1), tech('chain3', 2), tech('side', 1), tech('z')],
    { chain2: 'chain1', chain3: 'chain1', side: 'chain1' });
  data.localization.en.chain2.text = 'Zulu'; data.localization.en.chain3.text = 'Alpha';
  data.localization.ru.chain2.text = 'Альфа'; data.localization.ru.chain3.text = 'Ясень';
  data.localization.en.chain1.text = 'Zulu'; data.localization.en.z.text = 'Alpha';
  data.localization.ru.chain1.text = 'Альфа'; data.localization.ru.z.text = 'Ясень';
  const en = sttvLayout(data, 'en'), ru = sttvLayout(data, 'ru');
  assert.deepEqual(en.areas[0].cards.map(c => c.id), ['z', 'chain1', 'chain3', 'chain2', 'side']);
  assert.deepEqual(ru.areas[0].cards.map(c => c.id), ['chain1', 'chain2', 'chain3', 'side', 'z']);
  data.technologies = Object.fromEntries(Object.entries(data.technologies).reverse());
  for (const technology of Object.values(data.technologies)) technology.tree.children.reverse();
  assert.deepEqual(positions(sttvLayout(data, 'en')), positions(en));
  data.localization.en.chain2.text = 'Same'; data.localization.en.chain3.text = 'Same';
  assert.deepEqual(sttvLayout(data, 'en').areas[0].cards.slice(2, 4).map(c => c.id), ['chain2', 'chain3']);
});

test('the saved variant selects the area and uses the same localized name as the card', () => {
  const node = tech('base'); node.value!.items!.push(sttvVariant('base', 'society'));
  const data = catalog([node]); data.treeCombination.parameters.variants.base = 'swap:1';
  const layout = sttvLayout(data, 'en');
  assert.equal(layout.areas[0].cards.length, 0); assert.equal(layout.areas[1].cards[0].id, 'base');
  const text = sttvCreateTextLookup(data, 'en');
  const representation = sttvRepresentation(data.technologies.base, data.treeCombination.parameters.variants);
  assert.equal(text(sttvTechnologyName(data.technologies.base, representation, text)), 'base (Variant 1)');
});

test('ambiguous roots remain visible and diagnostics include the complete field context', () => {
  const data = catalog([tech('a'), tech('b', 1)], { b: 'a' }); data.technologies.a.tree.status = 'ambiguous';
  const layout = sttvLayout(data, 'en');
  assert.equal(layout.areas[0].cards.length, 2);
  const warning = layout.diagnostics[0];
  assert.equal(warning.severity, 'warning'); assert.equal(warning.details.language, 'en');
  assert.deepEqual(warning.details.sourceRef, data.technologies.a.sourceRef);
  assert.deepEqual(warning.details.combination, data.treeCombination); assert.ok(warning.details.settings);
});

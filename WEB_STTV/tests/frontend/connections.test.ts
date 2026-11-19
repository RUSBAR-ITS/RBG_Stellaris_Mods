import test from 'node:test';
import assert from 'node:assert/strict';
import { sttvAdaptDatabase } from '../../src/frontend/data/adapter';
import { sttvLayout } from '../../src/frontend/data/tree/layout';
import { sttvConnectAreas } from '../../src/frontend/data/connections/layout';
import { sttvConnectionRole } from '../../src/frontend/data/connections/segments';
import { sttvValidateConnections } from '../../src/frontend/data/connections/validation';
import { sttvAttachment } from '../../src/frontend/data/connections/points';
import { sttvPlaceTrees } from '../../src/frontend/data/tree/placement';
import { SttvPreparationError } from '../../src/frontend/workers/diagnostics';
import config from '../../config/frontend/connections.json';
import dimensions from '../../config/frontend/interface.json';
import { sttvCombination, sttvConnect } from './treeFixtures';
import { sttvDatabase, sttvTechnology } from './fixtures';

function prepare(tiers: Record<string, number>, parents: Record<string, string | null>) {
  const nodes = Object.entries(tiers).map(([id, tier]) => sttvTechnology(id, tier));
  sttvConnect(nodes, parents);
  const data = { ...sttvAdaptDatabase(sttvDatabase(nodes)), treeCombination: sttvCombination(Object.keys(tiers)) };
  return { data, layout: sttvLayout(data, 'en') };
}
const pairs = (routes: { parent: string; child: string }[]) => routes.map(r => [r.parent, r.child] as [string, string]);

test('attachments handle horizontal directions, shared side trunks and occupied incoming sides', () => {
  const { layout } = prepare({ P: 0, A: 1, B: 2, C: 1, D: 2, E: 1 }, { A: 'P', B: 'A', C: 'A', D: 'C', E: 'A' });
  const geometry = layout.areas[0].geometry;
  const route = (id: string) => geometry.routes.find(r => r.child === id)!;
  assert.deepEqual([route('B').source, route('B').target], ['right', 'left']);
  for (const id of ['C', 'E']) assert.deepEqual([route(id).source, route(id).target], ['bottom', 'left']);
  assert.ok(geometry.segments.some(s => s.parent === 'A' && s.children.includes('C') && s.children.includes('E')));
  assert.ok(geometry.junctions.some(j => j.parent === 'A'));
  const backwards = prepare({ A: 3, B: 4, C: 3 }, { B: 'A', C: 'B' }).layout.areas[0].geometry;
  assert.deepEqual([backwards.routes[1].source, backwards.routes[1].target], ['bottom', 'right']);
  assert.deepEqual(backwards.routes[1].points.at(-1), sttvAttachment(backwards.cards.C, 'right'));
});

test('a sole adjacent same-column child uses bottom/top and a mixed root uses a left trunk', () => {
  const single = prepare({ A: 0, B: 0 }, { B: 'A' }).layout;
  assert.deepEqual(single.areas[0].geometry.routes.map(r => [r.source, r.target]), [['bottom', 'top']]);
  assert.equal(single.report.connections.leftPadding, dimensions.fieldPadding);
  const mixed = prepare({ A: 0, B: 1, C: 0, E: 0 }, { B: 'A', C: 'A', E: 'A' }).layout;
  for (const r of mixed.areas[0].geometry.routes.filter(r => ['C', 'E'].includes(r.child)))
    assert.deepEqual([r.source, r.target], ['left', 'left']);
});

test('highlight membership selects the complete path without selecting sibling branches or descendants', () => {
  const geometry = prepare({ A: 0, B: 1, C: 1, D: 2 }, { B: 'A', C: 'A', D: 'B' }).layout.areas[0].geometry;
  assert.ok(geometry.segments.some(s => s.children.length === 2));
  for (const s of geometry.segments) {
    assert.equal(sttvConnectionRole(s.parent, s.children, 'B'), s.parent === 'B' ? 'children' : s.children.includes('B') ? 'parent' : 'default');
    assert.equal(sttvConnectionRole(s.parent, s.children, null), 'default');
    assert.equal(sttvConnectionRole(s.parent, s.children, 'A'), s.parent === 'A' ? 'children' : 'default');
  }
  assert.ok(geometry.segments.some(s => s.parent === 'A' && !s.children.includes('B') && sttvConnectionRole(s.parent, s.children, 'B') === 'default'));
});

test('children on opposite sides share the same exit corner without a displaced junction', () => {
  const g = prepare({ P: 0, A: 1, B: 1, C: 0 }, { A: 'P', B: 'A', C: 'A' }).layout.areas[0].geometry;
  const b = g.routes.find(r => r.child === 'B')!, c = g.routes.find(r => r.child === 'C')!;
  assert.deepEqual(b.points.slice(0, 2), c.points.slice(0, 2));
  const turn = b.points[2];
  assert.ok(g.junctions.some(j => j.parent === 'A' && j.x === turn.x && j.y === turn.y));
  assert.ok(!g.junctions.some(j => j.parent === 'A' && j.x === b.points[0].x));
});

test('expansion preserves logical placement, independent trees reuse gaps, and output is reproducible', () => {
  const { data, layout } = prepare({ A: 0, B: 1, C: 0, D: 0, E: 0, F: 2 },
    { B: 'A', C: 'A', D: 'C', E: 'A', F: 'D' });
  const repeated = sttvLayout(data, 'en');
  assert.deepEqual(repeated.areas, layout.areas);
  assert.equal(layout.report.connections.logicalConnections, 5);
  for (const area of layout.areas) for (const card of area.cards) {
    assert.equal(area.geometry.cards[card.id].width, dimensions.cardWidth);
    assert.equal(area.geometry.cards[card.id].height, dimensions.cardHeight);
    assert.equal(area.geometry.cards[card.id].x, layout.columns[card.column]);
  }
  assert.ok(layout.report.connections.leftPadding >= dimensions.fieldPadding);
  const area = layout.areas[0], parents = Object.fromEntries(Object.values(data.technologies).map(t => [t.id, t.tree.parent_tech]));
  const duplicate = { area: 'society', roots: area.roots.map(id => `copy_${id}`), rowCount: area.rowCount,
    cards: area.cards.map(c => ({ ...c, id: `copy_${c.id}` })) };
  const copiedParents = Object.fromEntries(Object.entries(parents).map(([id, parent]) => [`copy_${id}`, parent ? `copy_${parent}` : null]));
  const both = sttvConnectAreas([area, duplicate], { ...parents, ...copiedParents }, layout.tiers.length);
  assert.deepEqual(both.report.columnGaps, layout.report.connections.columnGaps);
  assert.equal(both.report.leftPadding, layout.report.connections.leftPadding);
});

test('independent geometry validation rejects card penetration, foreign overlaps and missing edges', () => {
  const original = prepare({ A: 0, B: 1, C: 2 }, { B: 'A', C: 'B' }).layout.areas[0].geometry;
  const expected = pairs(original.routes);
  const assertFailure = (geometry: typeof original) => assert.throws(() => sttvValidateConnections(geometry, expected),
    (error: unknown) => error instanceof SttvPreparationError && error.diagnostic.code === 'tree_connections_failed');
  const missing = structuredClone(original); missing.routes.pop(); assertFailure(missing);
  const crossing = structuredClone(original);
  const s = crossing.segments[0];
  crossing.segments.push({ ...s, id: 'foreign', parent: 'B' }); assertFailure(crossing);
  const card = structuredClone(original);
  card.routes[0].points.splice(1, 0, { x: card.cards.A.x, y: card.cards.A.y + card.cards.A.height / 2 });
  assertFailure(card);
});

test('routing exhaustion produces bounded, contextual diagnostics', () => {
  const area = { area: 'physics', roots: ['A'], rowCount: 1,
    cards: [{ id: 'A', column: 0, row: 0 }, { id: 'B', column: 0, row: 0 }] };
  assert.throws(() => sttvConnectAreas([area], { A: null, B: 'A' }, 1, { ...config, maxLaneAttempts: 1 }),
    (error: unknown) => error instanceof SttvPreparationError && error.diagnostic.details.parent === 'A'
      && error.diagnostic.details.child === 'B' && !!error.diagnostic.details.settings);
});

test('varied nested trees bridge crossings while retaining the original placement', () => {
  let seed = 109;
  const random = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 2 ** 32; };
  for (let example = 0; example < 20; example++) {
    const nodes = new Map<string, { column: number; children: string[] }>(), parents: Record<string, string | null> = {};
    for (let i = 0; i < 16; i++) {
      const id = `n${i}`;
      nodes.set(id, { column: Math.floor(random() * 5), children: [] });
      parents[id] = i ? `n${Math.floor(random() * i)}` : null;
      if (parents[id]) nodes.get(parents[id]!)!.children.push(id);
    }
    const placed = sttvPlaceTrees(['n0'], nodes, () => (a, b) => a.localeCompare(b));
    const area = { ...placed, area: 'physics', roots: ['n0'] };
    const result = sttvConnectAreas([area], parents, 5);
    assert.deepEqual(result.areas[0].cards, placed.cards);
    assert.equal(result.report.logicalConnections, 15);
    sttvValidateConnections(result.areas[0].geometry, Object.entries(parents).filter(([, p]) => p).map(([id, p]) => [p!, id]));
  }
});

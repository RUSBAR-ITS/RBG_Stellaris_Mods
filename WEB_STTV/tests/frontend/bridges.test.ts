import test from 'node:test';
import assert from 'node:assert/strict';
import { sttvCrossings, sttvBridges } from '../../src/frontend/data/connections/crossings';
import { sttvValidateBridges } from '../../src/frontend/data/connections/bridgeValidation';
import { sttvBridgePath, sttvSegmentPath } from '../../src/frontend/data/connections/paths';
import { sttvConnectionSegments } from '../../src/frontend/data/connections/segments';
import { sttvJoinTrunk } from '../../src/frontend/data/connections/candidates';
import type { SttvAreaConnections, SttvConnectionSegment, SttvRoute } from '../../src/frontend/data/connections/model';
import config from '../../config/frontend/connections.json';

const segment = (id: string, x1: number, y1: number, x2: number, y2: number): SttvConnectionSegment =>
  ({ id, parent: id, children: [`child_${id}`], from: { x: x1, y: y1 }, to: { x: x2, y: y2 } });
function geometry(segments = [segment('h', -100, 0, 100, 0), segment('v', 0, -100, 0, 100)]): SttvAreaConnections {
  const crossings = sttvCrossings(segments);
  return { segments, crossings, bridges: sttvBridges(crossings, config), cards: {}, routes: [], junctions: [],
    height: 200, rowGaps: [], topPadding: 0, bottomPadding: 0 };
}

test('perpendicular crossings have one bridge, while endpoints and coincident foreign lines are rejected', () => {
  const g = geometry();
  assert.equal(g.crossings.length, 1); assert.equal(g.bridges.length, 1);
  sttvValidateBridges(g, config);
  for (const other of [segment('v', 0, 0, 0, 100), segment('v', -50, 0, 50, 0)])
    assert.throws(() => geometry([g.segments[0], other]), /tree_connections_failed/);
});

test('the horizontal curve stays continuous and upward in either travel direction', () => {
  const g = geometry(), b = g.bridges[0];
  for (const direction of [1, -1]) {
    const s = direction === 1 ? g.segments[0] : { ...g.segments[0], from: g.segments[0].to, to: g.segments[0].from };
    const path = sttvSegmentPath(s, g.bridges), arc = sttvBridgePath(b, direction);
    assert.equal((path.match(/M/g) ?? []).length, 1);
    assert.equal((path.match(/C/g) ?? []).length, 2);
    assert.ok(path.includes(`${b.x},${b.y - b.height}`));
    assert.ok(path.startsWith(`M${s.from.x},${s.from.y}L${arc.start.x},${arc.start.y}C`));
    assert.ok(path.endsWith(`${arc.end.x},${arc.end.y}L${s.to.x},${s.to.y}`));
  }
  assert.equal(sttvSegmentPath(g.segments[1], g.bridges), 'M0,-100L0,100');
});

test('separate crossings keep separate bridges and reject insufficient space or nearby geometry', () => {
  const g = geometry([segment('h', -100, 0, 100, 0), segment('v', -30, -100, -30, 100), segment('w', 30, -100, 30, 100)]);
  sttvValidateBridges(g, config); assert.equal(g.bridges.length, 2);
  assert.equal((sttvSegmentPath(g.segments[0], g.bridges).match(/C/g) ?? []).length, 4);
  const tooClose = geometry([segment('h', -100, 0, 100, 0), segment('v', -10, -100, -10, 100), segment('w', 10, -100, 10, 100)]);
  assert.throws(() => sttvValidateBridges(tooClose, config), /tree_connections_failed/);
  const nearCorner = geometry([segment('h', -10, 0, 100, 0), segment('v', 0, -100, 0, 100)]);
  assert.throws(() => sttvValidateBridges(nearCorner, config), /tree_connections_failed/);
  const card = geometry(); card.cards.c = { id: 'c', x: -2, y: -10, width: 4, height: 4 };
  assert.throws(() => sttvValidateBridges(card, config), /tree_connections_failed/);
  const junction = geometry(); junction.junctions.push({ x: 5, y: -5, parent: 'h', children: [] });
  assert.throws(() => sttvValidateBridges(junction, config), /tree_connections_failed/);
});

test('joining a trunk at an interior contact reuses the prefix instead of creating a cycle', () => {
  const old: SttvRoute = { parent: 'p', child: 'a', source: 'right', target: 'left',
    points: [{ x: 0, y: 0 }, { x: 40, y: 0 }, { x: 40, y: 80 }, { x: 100, y: 80 }] };
  const joined = sttvJoinTrunk([{ x: 0, y: 0 }, { x: 20, y: 0 }, { x: 20, y: 40 }, { x: 100, y: 40 }], [old]);
  assert.deepEqual(joined, [{ x: 0, y: 0 }, { x: 40, y: 0 }, { x: 40, y: 40 }, { x: 100, y: 40 }]);
  const { segments, junctions } = sttvConnectionSegments([old, { ...old, child: 'b', points: joined }]);
  assert.equal(junctions.length, 1); assert.deepEqual([junctions[0].x, junctions[0].y], [40, 40]);
  assert.equal(sttvCrossings(segments).length, 0);
});

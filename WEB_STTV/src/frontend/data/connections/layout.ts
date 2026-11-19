import defaultDimensions from '../../../../config/frontend/interface.json';
import defaults from '../../../../config/frontend/connections.json';
import type { SttvAreaConnections, SttvConnectionArea, SttvConnectionSettings, SttvConnectionSummary } from './model';
import { sttvRouteArea } from './routing';
import { sttvConnectionAxis } from './axis';
import { sttvConnectionSegments } from './segments';
import { sttvValidateConnections } from './validation';
import { sttvTreeError } from '../tree/contract';
import { sttvCrossings, sttvBridges } from './crossings';
import { sttvRouteLength } from './candidates';

export function sttvConnectAreas<T extends SttvConnectionArea>(areas: T[], parents: Record<string, string | null>, columns: number,
  settings: SttvConnectionSettings = defaults, dimensions = defaultDimensions) {
  const start = performance.now();
  if (Object.values(settings).some(v => !Number.isFinite(v) || v <= 0)
    || !Number.isInteger(settings.maxLaneAttempts) || settings.bridgeUnderlayWidth <= settings.strokeWidth
    || settings.laneSpacing < settings.junctionRadius * 2 + settings.strokeWidth)
    sttvTreeError('tree_connections_failed', 'Invalid connection settings.', { settings });
  const routed = areas.map(area => {
    const result = sttvRouteArea(area, parents, columns, settings);
    return { ...result, rawCrossings: sttvCrossings(sttvConnectionSegments(result.routes).segments) };
  });
  const horizontal = (values: number[], reserved?: number[], crossings: number[] = []) => sttvConnectionAxis(columns, dimensions.cardWidth,
    dimensions.columnGap, dimensions.fieldPadding, dimensions.fieldPadding, values, settings, reserved, crossings);
  const treeByCard = new Map<string, string>(), treeValues = new Map<string, number[]>(), treeCrossings = new Map<string, number[]>();
  for (const area of routed) {
    let root = '';
    for (const card of area.cards) {
      if (area.roots.includes(card.id)) root = card.id;
      treeByCard.set(card.id, root);
      if (!treeValues.has(root)) { treeValues.set(root, []); treeCrossings.set(root, []); }
    }
    for (const route of area.routes) treeValues.get(treeByCard.get(route.parent)!)!.push(...route.points.map(p => p.x));
    for (const cross of area.rawCrossings) treeCrossings.get(treeByCard.get(cross.horizontalParent)!)!.push(cross.x);
  }
  // Independent trees reuse horizontal lanes instead of accumulating their widths.
  const reserved = horizontal([]).gaps;
  for (const [root, values] of treeValues) horizontal(values, undefined, treeCrossings.get(root)).gaps.forEach((gap, i) => reserved[i] = Math.max(reserved[i], gap));
  const x = horizontal([], reserved);
  const treeAxes = new Map([...treeValues].map(([root, values]) => [root, horizontal(values, reserved, treeCrossings.get(root))]));
  const result = routed.map(area => {
    const y = sttvConnectionAxis(area.rowCount, dimensions.cardHeight, dimensions.cardGap, 0, 0,
      area.routes.flatMap(r => r.points.map(p => p.y)), settings, undefined, area.rawCrossings.map(c => c.y), false);
    const cards = Object.fromEntries(area.cards.map(card => [card.id, { id: card.id, x: x.positions[card.column],
      y: y.positions[card.row], width: dimensions.cardWidth, height: dimensions.cardHeight }]));
    const routes = area.routes.map(route => ({ ...route, points: route.points.map(p =>
      ({ x: treeAxes.get(treeByCard.get(route.parent)!)!.pixel(p.x), y: y.pixel(p.y) })) }));
    const segments = sttvConnectionSegments(routes), crossings = sttvCrossings(segments.segments);
    const geometry: SttvAreaConnections = { cards, routes, ...segments, crossings, bridges: sttvBridges(crossings, settings), height: y.extent,
      rowGaps: y.gaps.slice(1, -1), topPadding: y.gaps[0], bottomPadding: y.gaps.at(-1)! };
    const expected = area.cards.filter(c => parents[c.id] && cards[parents[c.id]!]).map(c => [parents[c.id]!, c.id] as [string, string]);
    sttvValidateConnections(geometry, expected, settings);
    const { rectangles: _rectangles, routes: _routes, rawCrossings: _crossings, ...original } = area;
    return { ...original, geometry, height: dimensions.areaHeadingHeight + dimensions.tierHeadingHeight + y.extent };
  });
  const report: SttvConnectionSummary = { settings, logicalConnections: result.reduce((n, a) => n + a.geometry.routes.length, 0),
    crossings: result.reduce((n, a) => n + a.geometry.crossings.length, 0), bridges: result.reduce((n, a) => n + a.geometry.bridges.length, 0),
    bends: result.reduce((n, a) => n + a.geometry.routes.reduce((sum, r) => sum + r.points.length - 2, 0), 0),
    maxBends: Math.max(0, ...result.flatMap(a => a.geometry.routes.map(r => r.points.length - 2))),
    logicalPathLength: result.reduce((n, a) => n + a.geometry.routes.reduce((sum, r) => sum + sttvRouteLength(r.points), 0), 0),
    segments: result.reduce((n, a) => n + a.geometry.segments.length, 0), junctions: result.reduce((n, a) => n + a.geometry.junctions.length, 0),
    columnGaps: x.gaps.slice(1, -1), leftPadding: x.gaps[0], rightPadding: x.gaps.at(-1)!,
    areas: result.map(a => ({ area: a.area, rowGaps: a.geometry.rowGaps, topPadding: a.geometry.topPadding,
      bottomPadding: a.geometry.bottomPadding, connections: a.geometry.routes.length })), seconds: (performance.now() - start) / 1000 };
  return { areas: result, columns: x.positions, width: x.extent, report };
}

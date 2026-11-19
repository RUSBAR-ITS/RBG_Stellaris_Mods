import type { SttvConnectionSegment, SttvJunction, SttvPoint, SttvRoute } from './model';
import { sttvPointKey } from './points';

export function sttvConnectionSegments(routes: SttvRoute[]) {
  type Interval = { low: number; high: number; child: string };
  const lines = new Map<string, { parent: string; horizontal: boolean; fixed: number; intervals: Interval[] }>();
  for (const route of routes) for (let i = 1; i < route.points.length; i++) {
    const a = route.points[i - 1], b = route.points[i], horizontal = a.y === b.y;
    const fixed = horizontal ? a.y : a.x, from = horizontal ? a.x : a.y, to = horizontal ? b.x : b.y;
    const key = JSON.stringify([route.parent, horizontal, fixed]);
    if (!lines.has(key)) lines.set(key, { parent: route.parent, horizontal, fixed, intervals: [] });
    lines.get(key)!.intervals.push({ low: Math.min(from, to), high: Math.max(from, to), child: route.child });
  }
  const segments: SttvConnectionSegment[] = [];
  for (const line of lines.values()) {
    const ends = [...new Set(line.intervals.flatMap(i => [i.low, i.high]))].sort((a, b) => a - b);
    for (let i = 1; i < ends.length; i++) {
      const low = ends[i - 1], high = ends[i];
      const children = [...new Set(line.intervals.filter(v => v.low <= low && v.high >= high).map(v => v.child))].sort();
      if (!children.length) continue;
      const point = (v: number): SttvPoint => line.horizontal ? { x: v, y: line.fixed } : { x: line.fixed, y: v };
      segments.push({ id: `sttv-segment-${segments.length}`, parent: line.parent, children, from: point(low), to: point(high) });
    }
  }
  const endpoints = new Map<string, { point: SttvPoint; parent: string; segments: SttvConnectionSegment[] }>();
  for (const segment of segments) for (const point of [segment.from, segment.to]) {
    const key = JSON.stringify([segment.parent, sttvPointKey(point)]);
    if (!endpoints.has(key)) endpoints.set(key, { point, parent: segment.parent, segments: [] });
    endpoints.get(key)!.segments.push(segment);
  }
  const junctions: SttvJunction[] = [...endpoints.values()].filter(v => v.segments.length >= 3).map(v =>
    ({ ...v.point, parent: v.parent, children: [...new Set(v.segments.flatMap(s => s.children))].sort() }));
  return { segments, junctions };
}
export function sttvConnectionRole(parent: string, children: string[], hovered: string | null) {
  return hovered === parent ? 'children' : hovered !== null && children.includes(hovered) ? 'parent' : 'default';
}

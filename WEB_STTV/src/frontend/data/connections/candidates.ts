import type { SttvPoint, SttvRectangle, SttvRoute } from './model';
import { sttvCardContact, sttvProperCrossing } from './contact';
import { sttvIntersects, sttvOnSegment, sttvSamePoint, sttvSimplify } from './points';

export function sttvJoinTrunk(points: SttvPoint[], existing: SttvRoute[]) {
  for (let i = points.length - 1; i > 0; i--) {
    const a = points[i - 1], b = points[i];
    const hits: { point: SttvPoint; prefix: SttvPoint[]; distance: number }[] = [];
    for (const route of existing) for (let j = 1; j < route.points.length; j++) {
      const c = route.points[j - 1], d = route.points[j], crossing = sttvProperCrossing(a, b, c, d);
      const contacts = crossing ? [crossing] : [a, b, c, d].filter(p => sttvOnSegment(p, a, b) && sttvOnSegment(p, c, d));
      for (const point of contacts) hits.push({ point, prefix: route.points.slice(0, j), distance: Math.abs(b.x - point.x) + Math.abs(b.y - point.y) });
    }
    const hit = hits.sort((a, b) => a.distance - b.distance)[0];
    if (hit) return sttvSimplify([...hit.prefix, hit.point, ...points.slice(i)]);
  }
  return points;
}
function outside(a: SttvPoint, b: SttvPoint, side: SttvRoute['source']) {
  return side === 'left' ? b.x < a.x && b.y === a.y : side === 'right' ? b.x > a.x && b.y === a.y
    : side === 'bottom' ? b.y > a.y && b.x === a.x : b.y < a.y && b.x === a.x;
}
export function sttvCandidateConflict(route: SttvRoute, cards: SttvRectangle[], existing: SttvRoute[]) {
  const { points } = route;
  if (points.length < 2 || !outside(points[0], points[1], route.source)
    || !outside(points.at(-1)!, points.at(-2)!, route.target)) return { reason: 'attachment' };
  for (let i = 1; i < points.length; i++) {
    const a = points[i - 1], b = points[i];
    if (a.x !== b.x && a.y !== b.y || sttvSamePoint(a, b)) return { reason: 'segment' };
    for (let j = 1; j < i - 1; j++) if (sttvIntersects(a, b, points[j - 1], points[j])) return { reason: 'self_intersection' };
    for (const card of cards) {
      const hit = sttvCardContact(a, b, card);
      if (hit && !(hit.single && (card.id === route.parent && i === 1 && sttvSamePoint(hit.point, points[0])
        || card.id === route.child && i === points.length - 1 && sttvSamePoint(hit.point, points.at(-1)!)))) return { reason: 'card', card: card.id };
    }
    for (const old of existing) for (let j = 1; j < old.points.length; j++) {
      const c = old.points[j - 1], d = old.points[j];
      if (!sttvIntersects(a, b, c, d)) continue;
      if (old.parent === route.parent && old.source === route.source) continue;
      if (old.parent === route.parent || !sttvProperCrossing(a, b, c, d)) return { reason: 'route', other: old, segment: [a, b], contact: [c, d] };
    }
  }
  return null;
}
export function sttvCrossingCount(route: SttvRoute, existing: SttvRoute[]) {
  const crossings = new Set<string>();
  for (const old of existing) {
    if (old.parent === route.parent) continue;
    for (let i = 1; i < route.points.length; i++) for (let j = 1; j < old.points.length; j++) {
      const point = sttvProperCrossing(route.points[i - 1], route.points[i], old.points[j - 1], old.points[j]);
      if (point) crossings.add(JSON.stringify([old.parent, point.x, point.y]));
    }
  }
  return crossings.size;
}
export function sttvRouteLength(points: SttvPoint[]) {
  return points.slice(1).reduce((sum, p, i) => sum + Math.abs(p.x - points[i].x) + Math.abs(p.y - points[i].y), 0);
}

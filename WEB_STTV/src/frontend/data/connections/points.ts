import type { SttvPoint, SttvRectangle, SttvSide } from './model';

export const sttvPointKey = (p: SttvPoint) => `${p.x}:${p.y}`;
export const sttvSamePoint = (a: SttvPoint, b: SttvPoint) => a.x === b.x && a.y === b.y;
export function sttvAttachment(rect: SttvRectangle, side: SttvSide): SttvPoint {
  return { x: rect.x + (side === 'left' ? 0 : side === 'right' ? rect.width : rect.width / 2),
    y: rect.y + (side === 'top' ? 0 : side === 'bottom' ? rect.height : rect.height / 2) };
}
export function sttvOnSegment(p: SttvPoint, a: SttvPoint, b: SttvPoint) {
  return (a.x === b.x && p.x === a.x || a.y === b.y && p.y === a.y)
    && p.x >= Math.min(a.x, b.x) && p.x <= Math.max(a.x, b.x)
    && p.y >= Math.min(a.y, b.y) && p.y <= Math.max(a.y, b.y);
}
export function sttvSimplify(points: SttvPoint[]) {
  const result: SttvPoint[] = [];
  for (const point of points) {
    if (result.length && sttvSamePoint(result.at(-1)!, point)) continue;
    while (result.length > 1) {
      const a = result.at(-2)!, b = result.at(-1)!;
      if (!sttvOnSegment(b, a, point)) break;
      result.pop();
    }
    result.push(point);
  }
  return result;
}
export function sttvIntersects(a: SttvPoint, b: SttvPoint, c: SttvPoint, d: SttvPoint) {
  if (a.x === b.x && c.y === d.y) return sttvOnSegment({ x: a.x, y: c.y }, a, b)
    && sttvOnSegment({ x: a.x, y: c.y }, c, d);
  if (a.y === b.y && c.x === d.x) return sttvIntersects(c, d, a, b);
  return sttvOnSegment(a, c, d) || sttvOnSegment(b, c, d) || sttvOnSegment(c, a, b) || sttvOnSegment(d, a, b);
}

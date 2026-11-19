import type { SttvPoint, SttvRectangle } from './model';
import { sttvIntersects } from './points';

export function sttvCardContact(a: SttvPoint, b: SttvPoint, rect: SttvRectangle) {
  const vertical = a.x === b.x, fixed = vertical ? a.x : a.y;
  const edge = vertical ? rect.x : rect.y, size = vertical ? rect.width : rect.height;
  if (fixed < edge || fixed > edge + size) return null;
  const start = vertical ? rect.y : rect.x, length = vertical ? rect.height : rect.width;
  const low = Math.max(Math.min(vertical ? a.y : a.x, vertical ? b.y : b.x), start);
  const high = Math.min(Math.max(vertical ? a.y : a.x, vertical ? b.y : b.x), start + length);
  return low <= high ? { single: low === high, point: vertical ? { x: fixed, y: low } : { x: low, y: fixed } } : null;
}
export function sttvProperCrossing(a: SttvPoint, b: SttvPoint, c: SttvPoint, d: SttvPoint): SttvPoint | null {
  if ((a.y === b.y) === (c.y === d.y) || !sttvIntersects(a, b, c, d)) return null;
  const h = a.y === b.y ? [a, b] : [c, d], v = a.y === b.y ? [c, d] : [a, b];
  const p = { x: v[0].x, y: h[0].y };
  return p.x > Math.min(h[0].x, h[1].x) && p.x < Math.max(h[0].x, h[1].x)
    && p.y > Math.min(v[0].y, v[1].y) && p.y < Math.max(v[0].y, v[1].y) ? p : null;
}

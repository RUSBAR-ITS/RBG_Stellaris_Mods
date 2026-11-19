import type { SttvPoint, SttvRoute } from './model';
import { sttvSimplify } from './points';

// Normalized cells are independent of pixel dimensions. Lanes occupy gaps only.
export const sttvCell = 10, sttvBandStart = 2, sttvBandSize = 6;
export function sttvLanes(columns: number, top: number, bottom: number) {
  const lanes = new Map<string, number>(), counts = new Map<string, number>();
  return (axis: 'x' | 'y', gap: number, owner: string) => {
    const key = `${axis}:${gap}:${owner}`;
    if (!lanes.has(key)) {
      const group = `${axis}:${gap}`, n = counts.get(group) ?? 0;
      const first = axis === 'x' ? 0 : top, last = axis === 'x' ? columns : bottom;
      const step = Math.ceil(n / 2), interior = (n % 2 ? 1 : -1) * step / (step + 1);
      const offset = gap === first ? 1 + n / (n + 1) / 2 : gap === last ? -1 - n / (n + 1) / 2 : interior;
      lanes.set(key, gap * sttvCell + offset); counts.set(group, n + 1);
    }
    return lanes.get(key)!;
  };
}
export function sttvTemplates(a: SttvPoint, b: SttvPoint, source: SttvRoute['source'], target: SttvRoute['target'],
  trunk: number, entry: number, departures: number[]) {
  const result: SttvPoint[][] = [[a, b]];
  if (target === 'top') return result;
  if (source === 'bottom') {
    result.push([a, { x: a.x, y: b.y }, b]);
    for (const y of departures) for (const x of [trunk, entry])
      result.push([a, { x: a.x, y }, { x, y }, { x, y: b.y }, b]);
  } else {
    for (const x of [trunk, entry]) result.push([a, { x, y: a.y }, { x, y: b.y }, b]);
    for (const y of departures) result.push([a, { x: trunk, y: a.y }, { x: trunk, y }, { x: entry, y }, { x: entry, y: b.y }, b]);
  }
  return result.map(sttvSimplify);
}

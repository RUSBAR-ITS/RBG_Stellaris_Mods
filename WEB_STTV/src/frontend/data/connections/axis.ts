import type { SttvConnectionSettings } from './model';

export function sttvConnectionAxis(count: number, cardSize: number, baseline: number, first: number, last: number,
  values: number[], settings: SttvConnectionSettings, reserved?: number[], crossings: number[] = [], horizontal = true) {
  const tracks = Array.from({ length: count + 1 }, () => new Set<number>());
  for (const value of values) {
    const band = value % 10;
    if (band >= 2 && band <= 8) continue;
    const gap = Math.floor((value + 2) / 10);
    if (gap >= 0 && gap <= count) tracks[gap].add(value);
  }
  const lanes = tracks.map(set => [...set].sort((a, b) => a - b));
  const clearance = Math.max(settings.cardClearance, settings.exitLength,
    settings.arrowSize / 2 + settings.strokeWidth, settings.junctionRadius + settings.strokeWidth);
  const affected = new Set(crossings.filter(value => value % 10 < 2 || value % 10 > 8).map(value => Math.floor((value + 2) / 10)));
  const bridgeSpace = horizontal ? settings.bridgeWidth : settings.bridgeHeight;
  const spacings = lanes.map((_, i) => affected.has(i)
    ? Math.max(settings.laneSpacing, bridgeSpace + settings.bridgeUnderlayWidth + 2 * settings.bridgeClearance + settings.bridgeSpacing) : settings.laneSpacing);
  const clearances = lanes.map((_, i) => affected.has(i) ? Math.max(clearance,
    (horizontal ? settings.bridgeWidth / 2 : settings.bridgeHeight) + settings.bridgeUnderlayWidth / 2 + settings.bridgeClearance + settings.arrowSize) : clearance);
  const gaps = lanes.map((lane, i) => Math.max(reserved?.[i] ?? 0, i === 0 ? first : i === count ? last : baseline,
    lane.length ? clearances[i] * 2 + (lane.length - 1) * spacings[i] : 0));
  const positions: number[] = [], mapping = new Map<number, number>();
  let cursor = 0;
  for (let i = 0; i <= count; i++) {
    const offset = (gaps[i] - Math.max(0, lanes[i].length - 1) * spacings[i]) / 2;
    lanes[i].forEach((lane, n) => mapping.set(lane, cursor + offset + n * spacings[i]));
    cursor += gaps[i];
    if (i < count) { positions.push(cursor); cursor += cardSize; }
  }
  function pixel(value: number) {
    const mapped = mapping.get(value);
    if (mapped !== undefined) return mapped;
    const cell = Math.floor(value / 10), band = value % 10;
    if (band >= 2 && band <= 8 && cell < count) return positions[cell] + (band - 2) * cardSize / 6;
    throw new Error(`Missing routing coordinate: ${value}`);
  }
  return { positions, gaps, extent: cursor, pixel };
}

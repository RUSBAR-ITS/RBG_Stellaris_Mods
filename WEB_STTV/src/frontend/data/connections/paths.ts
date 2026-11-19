import type { SttvBridge, SttvConnectionSegment } from './model';

export function sttvBridgePath(b: SttvBridge, direction = 1) {
  const start = b.x - direction * b.width / 2, end = b.x + direction * b.width / 2;
  const middle = b.x - direction * b.width / 4, other = b.x + direction * b.width / 4;
  return { start: { x: start, y: b.y }, end: { x: end, y: b.y },
    curve: `C${middle},${b.y} ${middle},${b.y - b.height} ${b.x},${b.y - b.height}C${other},${b.y - b.height} ${other},${b.y} ${end},${b.y}` };
}
export function sttvSegmentPath(segment: SttvConnectionSegment, bridges: SttvBridge[]) {
  const { from, to } = segment, direction = Math.sign(to.x - from.x);
  let path = `M${from.x},${from.y}`;
  for (const bridge of bridges.filter(b => b.horizontal === segment.id).sort((a, b) => (a.x - b.x) * direction)) {
    const arc = sttvBridgePath(bridge, direction);
    path += `L${arc.start.x},${arc.start.y}${arc.curve}`;
  }
  return `${path}L${to.x},${to.y}`;
}

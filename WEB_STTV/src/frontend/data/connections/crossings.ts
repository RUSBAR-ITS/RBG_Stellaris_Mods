import type { SttvConnectionSegment, SttvConnectionSettings, SttvCrossing } from './model';
import { sttvIntersects } from './points';
import { sttvProperCrossing } from './contact';
import { sttvTreeError } from '../tree/contract';

export function sttvCrossings(segments: SttvConnectionSegment[]) {
  const crossings: SttvCrossing[] = [];
  for (let i = 0; i < segments.length; i++) for (let j = i + 1; j < segments.length; j++) {
    const a = segments[i], b = segments[j];
    if (a.parent === b.parent || !sttvIntersects(a.from, a.to, b.from, b.to)) continue;
    const point = sttvProperCrossing(a.from, a.to, b.from, b.to);
    if (!point) sttvTreeError('tree_connections_failed', 'Foreign routes overlap or touch an endpoint.', { first: a, second: b });
    const [horizontal, vertical] = a.from.y === a.to.y ? [a, b] : [b, a];
    crossings.push({ ...point!, id: `sttv-crossing-${crossings.length}`, horizontal: horizontal.id, vertical: vertical.id,
      horizontalParent: horizontal.parent, verticalParent: vertical.parent });
  }
  return crossings;
}
export function sttvBridges(crossings: SttvCrossing[], settings: SttvConnectionSettings) {
  return crossings.map(crossing => ({ ...crossing, width: settings.bridgeWidth, height: settings.bridgeHeight, underlayWidth: settings.bridgeUnderlayWidth }));
}

import type { SttvAreaConnections } from './model';
import defaults from '../../../../config/frontend/connections.json';
import { sttvCrossings, sttvBridges } from './crossings';
import { sttvValidateBridges } from './bridgeValidation';
import { sttvCardContact } from './contact';
import { sttvAttachment, sttvSamePoint } from './points';
import { sttvTreeError } from '../tree/contract';

export function sttvValidateConnections(geometry: SttvAreaConnections, expected: [string, string][], settings = defaults) {
  const fail = (reason: string, details: Record<string, unknown>) => sttvTreeError('tree_connections_failed', reason, details);
  const keys = geometry.routes.map(r => JSON.stringify([r.parent, r.child]));
  if (new Set(keys).size !== keys.length || JSON.stringify([...keys].sort()) !== JSON.stringify(expected.map(v => JSON.stringify(v)).sort()))
    fail('Connection coverage differs from the selected tree.', { expected, received: keys });
  const rectangles = Object.values(geometry.cards);
  for (const route of geometry.routes) {
    const source = sttvAttachment(geometry.cards[route.parent], route.source), target = sttvAttachment(geometry.cards[route.child], route.target);
    if (route.points.length < 2 || !sttvSamePoint(source, route.points[0]) || !sttvSamePoint(target, route.points.at(-1)!))
      fail('Connection endpoint mismatch.', { route, source, target });
    for (let i = 1; i < route.points.length; i++) {
      const a = route.points[i - 1], b = route.points[i];
      if (![a.x, a.y, b.x, b.y].every(Number.isFinite) || (a.x !== b.x && a.y !== b.y) || sttvSamePoint(a, b))
        fail('Invalid orthogonal segment.', { route, segment: i });
      for (const rect of rectangles) {
        const hit = sttvCardContact(a, b, rect);
        if (!hit) continue;
        const allowed = hit.single && (rect.id === route.parent && i === 1 && sttvSamePoint(hit.point, source)
          || rect.id === route.child && i === route.points.length - 1 && sttvSamePoint(hit.point, target));
        if (!allowed) fail('Connection touches or crosses a card.', { route, card: rect, segment: i });
      }
    }
  }
  const crossings = sttvCrossings(geometry.segments);
  if (JSON.stringify(crossings) !== JSON.stringify(geometry.crossings)
    || JSON.stringify(sttvBridges(crossings, settings)) !== JSON.stringify(geometry.bridges))
    fail('Crossing or bridge coverage mismatch.', { crossings, bridges: geometry.bridges });
  sttvValidateBridges(geometry, settings);
}

import type { SttvAreaConnections, SttvConnectionSettings, SttvRectangle } from './model';
import { sttvCardContact } from './contact';
import { sttvTreeError } from '../tree/contract';

function overlap(a: SttvRectangle, b: SttvRectangle) {
  return a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height;
}
export function sttvValidateBridges(geometry: SttvAreaConnections, settings: SttvConnectionSettings) {
  const bounds = geometry.bridges.map(b => {
    const padding = b.underlayWidth / 2 + settings.bridgeClearance;
    return { id: b.id, x: b.x - b.width / 2 - padding, y: b.y - b.height - padding,
      width: b.width + padding * 2, height: b.height + padding * 2 };
  });
  const fail = (reason: string, details: Record<string, unknown>) => sttvTreeError('tree_connections_failed', reason, details);
  for (let i = 0; i < bounds.length; i++) {
    const bound = bounds[i], bridge = geometry.bridges[i];
    const horizontal = geometry.segments.find(s => s.id === bridge.horizontal)!;
    const vertical = geometry.segments.find(s => s.id === bridge.vertical)!;
    if (Math.min(Math.abs(bridge.x - horizontal.from.x), Math.abs(bridge.x - horizontal.to.x)) < bound.width / 2
      || bridge.y - Math.min(vertical.from.y, vertical.to.y) < bridge.y - bound.y
      || Math.max(vertical.from.y, vertical.to.y) - bridge.y < bound.y + bound.height - bridge.y)
      fail('Bridge clearance touches a segment endpoint or corner.', { bridge, horizontal, vertical });
    for (const card of Object.values(geometry.cards)) if (overlap(bound, card)) fail('Bridge clearance touches a card.', { bridge, card });
    for (const segment of geometry.segments) {
      if (segment.id === bridge.horizontal || segment.id === bridge.vertical) continue;
      if (sttvCardContact(segment.from, segment.to, bound)) fail('Bridge clearance touches another segment.', { bridge, segment });
    }
    for (const route of geometry.routes) {
      const tip = route.points.at(-1)!, previous = route.points.at(-2)!;
      const dx = Math.sign(tip.x - previous.x), dy = Math.sign(tip.y - previous.y), size = settings.arrowSize;
      const back = { x: tip.x - dx * size, y: tip.y - dy * size };
      const arrow = { id: route.child, x: Math.min(tip.x, back.x) - Math.abs(dy) * size / 2,
        y: Math.min(tip.y, back.y) - Math.abs(dx) * size / 2, width: (Math.abs(dx) || 1) * size, height: (Math.abs(dy) || 1) * size };
      if (overlap(bound, arrow)) fail('Bridge clearance touches an arrow.', { bridge, route });
    }
    for (const j of geometry.junctions) if (overlap(bound, { id: j.parent, x: j.x - settings.junctionRadius,
      y: j.y - settings.junctionRadius, width: 2 * settings.junctionRadius, height: 2 * settings.junctionRadius }))
      fail('Bridge clearance touches a junction.', { bridge, junction: j });
    for (let j = 0; j < i; j++) if (overlap(bound, bounds[j])) fail('Bridge clearances overlap.', { first: bridge, second: geometry.bridges[j] });
  }
}

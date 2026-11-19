import type { SttvConnectionArea, SttvConnectionSettings, SttvRoute, SttvSide } from './model';
import { sttvAttachment } from './points';
import { sttvLanes, sttvTemplates, sttvCell, sttvBandStart, sttvBandSize } from './templates';
import { sttvJoinTrunk, sttvCandidateConflict, sttvRouteLength, sttvCrossingCount } from './candidates';
import { sttvTreeError } from '../tree/contract';

export function sttvRouteArea<T extends SttvConnectionArea>(area: T, parents: Record<string, string | null>,
  columns: number, settings: SttvConnectionSettings) {
  const rectangles = Object.fromEntries(area.cards.map(card => [card.id, { id: card.id,
    x: card.column * sttvCell + sttvBandStart, y: card.row * sttvCell + sttvBandStart, width: sttvBandSize, height: sttvBandSize }]));
  const routes: SttvRoute[] = [], incoming = new Map<string, SttvSide>();
  const children = new Map(area.cards.map(card => [card.id, area.cards.filter(child => parents[child.id] === card.id)]));
  for (let root = 0; root < area.roots.length; root++) {
    const begin = area.cards.findIndex(card => card.id === area.roots[root]);
    const end = root + 1 < area.roots.length ? area.cards.findIndex(card => card.id === area.roots[root + 1]) : area.cards.length;
    const tree = area.cards.slice(begin, end), treeRoutes: SttvRoute[] = [];
    const lane = sttvLanes(columns, tree[0].row, Math.max(...tree.map(card => card.row)) + 1);
    const cards = tree.map(card => rectangles[card.id]);
    for (const parent of tree) for (const child of children.get(parent.id)!) {
      const vertical = parent.column === child.column && children.get(parent.id)!.length === 1 && child.row === parent.row + 1;
      const target: SttvSide = vertical ? 'top' : child.column < parent.column ? 'right' : 'left';
      let source: SttvSide = vertical ? 'bottom' : child.column > parent.column ? 'right' : 'left';
      if (incoming.get(parent.id) === source) source = 'bottom';
      const owner = `${parent.id}:${source}`, a = sttvAttachment(rectangles[parent.id], source), b = sttvAttachment(rectangles[child.id], target);
      let selected: SttvRoute | undefined;
      let rejected: unknown[] = [];
      for (let attempt = 0; attempt < settings.maxLaneAttempts && !selected; attempt++) {
        const key = `${owner}:${attempt}`;
        const trunk = lane('x', parent.column + Number(child.column > parent.column), key);
        const entry = lane('x', child.column + Number(target === 'right'), `${key}:entry`);
        const ys = [lane('y', parent.row + 1, key), lane('y', child.row, key)];
        const candidates = sttvTemplates(a, b, source, target, trunk, entry, ys).map(points => ({ parent: parent.id, child: child.id, source, target,
          points: sttvJoinTrunk(points, treeRoutes.filter(r => r.parent === parent.id && r.source === source)) }));
        candidates.sort((x, y) => x.points.length - y.points.length || sttvRouteLength(x.points) - sttvRouteLength(y.points)
          || sttvCrossingCount(x, treeRoutes) - sttvCrossingCount(y, treeRoutes));
        rejected = [];
        selected = candidates.find(route => {
          const conflict = sttvCandidateConflict(route, cards, treeRoutes);
          if (conflict) rejected.push(conflict);
          return !conflict;
        });
      }
      if (!selected) sttvTreeError('tree_connections_failed', 'No valid simple route found.',
        { area: area.area, parent: parent.id, child: child.id, source, target, settings, parentPosition: parent, childPosition: child, rejected });
      treeRoutes.push(selected!); incoming.set(child.id, target);
    }
    routes.push(...treeRoutes);
  }
  return { ...area, rectangles, routes };
}

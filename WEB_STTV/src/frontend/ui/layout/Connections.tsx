import type { SttvAreaConnections } from '../../data/connections/model';
import { sttvConnectionRole } from '../../data/connections/segments';
import { SttvConnection, SttvConnectionArrow, SttvConnectionBridge } from '../base/Connection';
import { sttvBridgePath, sttvSegmentPath } from '../../data/connections/paths';
import settings from '../../../../config/frontend/connections.json';
import './connections.css';

export function SttvConnections({ geometry, hovered, width }: { geometry: SttvAreaConnections; hovered: string | null; width: number }) {
  return <svg className="sttv-connections" width={width} height={geometry.height} aria-hidden="true" focusable="false">
    {geometry.segments.map(s => <SttvConnection key={s.id} {...s} path={sttvSegmentPath(s, geometry.bridges)} role={sttvConnectionRole(s.parent, s.children, hovered)} />)}
    {geometry.bridges.map(b => {
      const segment = geometry.segments.find(s => s.id === b.horizontal)!, arc = sttvBridgePath(b);
      return <SttvConnectionBridge key={b.id} id={b.id} path={`M${arc.start.x},${arc.start.y}${arc.curve}`}
        underlayWidth={b.underlayWidth} role={sttvConnectionRole(segment.parent, segment.children, hovered)} />;
    })}
    {geometry.junctions.map((j, i) => <circle key={i} className="sttv-connection-junction" cx={j.x} cy={j.y}
      r={settings.junctionRadius} data-parent={j.parent} data-children={JSON.stringify(j.children)}
      data-role={sttvConnectionRole(j.parent, j.children, hovered)} />)}
    {geometry.routes.map(r => <SttvConnectionArrow key={r.child} parent={r.parent} child={r.child}
      point={r.points.at(-1)!} previous={r.points.at(-2)!} role={sttvConnectionRole(r.parent, [r.child], hovered)} />)}
  </svg>;
}

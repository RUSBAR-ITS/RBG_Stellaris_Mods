import type { SttvPoint } from '../../data/connections/model';
import settings from '../../../../config/frontend/connections.json';

export type SttvConnectionRole = 'default' | 'parent' | 'children';
export function SttvConnection({ path, role, id, parent, children }:
  { path: string; role: SttvConnectionRole; id: string; parent: string; children: string[] }) {
  return <path className="sttv-connection" data-connection-segment={id} data-parent={parent}
    data-children={JSON.stringify(children)} data-role={role} d={path} />;
}
export function SttvConnectionBridge({ path, role, id, underlayWidth }:
  { path: string; role: SttvConnectionRole; id: string; underlayWidth: number }) {
  return <g data-connection-bridge={id} data-role={role}>
    <path className="sttv-bridge-underlay" d={path} style={{ strokeWidth: underlayWidth }} />
    <path className="sttv-connection sttv-bridge-stroke" d={path} />
  </g>;
}
export function SttvConnectionArrow({ point, previous, role, parent, child }:
  { point: SttvPoint; previous: SttvPoint; role: SttvConnectionRole; parent: string; child: string }) {
  const size = settings.arrowSize, dx = Math.sign(point.x - previous.x), dy = Math.sign(point.y - previous.y);
  const back = { x: point.x - dx * size, y: point.y - dy * size };
  return <path className="sttv-connection-arrow" data-role={role} data-connection-parent={parent} data-connection-child={child}
    d={`M${point.x},${point.y}L${back.x + dy * size / 2},${back.y - dx * size / 2}L${back.x - dy * size / 2},${back.y + dx * size / 2}Z`} />;
}

import type config from '../../../../config/frontend/connections.json';
import type { SttvPlacement } from '../tree/model';

export type SttvConnectionSettings = typeof config;
export type SttvPoint = { x: number; y: number };
export type SttvSide = 'left' | 'right' | 'top' | 'bottom';
export interface SttvRectangle extends SttvPoint { id: string; width: number; height: number }
export interface SttvRoute {
  parent: string; child: string; source: SttvSide; target: SttvSide; points: SttvPoint[];
}
export interface SttvConnectionSegment {
  id: string; parent: string; children: string[]; from: SttvPoint; to: SttvPoint;
}
export interface SttvJunction extends SttvPoint { parent: string; children: string[] }
export interface SttvCrossing extends SttvPoint { id: string; horizontal: string; vertical: string; horizontalParent: string; verticalParent: string }
export interface SttvBridge extends SttvCrossing { width: number; height: number; underlayWidth: number }
export interface SttvAreaConnections {
  cards: Record<string, SttvRectangle>;
  routes: SttvRoute[]; segments: SttvConnectionSegment[]; junctions: SttvJunction[];
  crossings: SttvCrossing[]; bridges: SttvBridge[];
  height: number; rowGaps: number[]; topPadding: number; bottomPadding: number;
}
export interface SttvConnectionArea {
  area: string; roots: string[]; cards: SttvPlacement[]; rowCount: number;
}
export interface SttvConnectionSummary {
  settings: SttvConnectionSettings; logicalConnections: number; segments: number; junctions: number;
  crossings: number; bridges: number; bends: number; maxBends: number; logicalPathLength: number;
  columnGaps: number[]; leftPadding: number; rightPadding: number;
  areas: { area: string; rowGaps: number[]; topPadding: number; bottomPadding: number; connections: number }[];
  seconds: number;
}

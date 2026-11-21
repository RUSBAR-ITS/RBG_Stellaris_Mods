import type { SttvArea } from '../model';
import type { SttvAreaConnections } from '../connections/model';

export interface SttvPlacement { id: string; column: number; row: number }
export interface SttvAreaLayout {
  area: SttvArea; roots: string[]; cards: SttvPlacement[]; rowCount: number; height: number; geometry: SttvAreaConnections;
}
export interface SttvLayout { areas: SttvAreaLayout[]; tiers: number[]; columns: number[]; width: number; height: number }

import type { ReactNode } from 'react';
import { SttvStatusPanel } from '../ui/composite/StatusPanel';
import type { SttvTextRef } from '../localization/model';
import './main-window.css';

export function SttvMainWindow({ menu, children, status }:
  { menu: ReactNode; children: ReactNode; status: SttvTextRef }) {
  return <div className="sttv-main-window">
    <div className="sttv-workspace">{menu}<main className="sttv-main-content">{children}</main></div>
    <SttvStatusPanel message={status} />
  </div>;
}

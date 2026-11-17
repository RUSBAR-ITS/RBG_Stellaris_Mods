import type { ReactNode } from 'react';
import './menu.css';

export function SttvMenuButtonGroup({ children }: { children: ReactNode }) {
  return <div className="sttv-menu-bottom">{children}</div>;
}
export function SttvMenuPanel({ expanded, actions, settings, buttons }:
  { expanded: boolean; actions: ReactNode; settings: ReactNode; buttons: ReactNode }) {
  return <aside className="sttv-menu-panel" data-expanded={expanded}>
    {expanded && <div className="sttv-menu-content">
      <div className="sttv-menu-actions">{actions}</div>{settings}
    </div>}
    <SttvMenuButtonGroup>{buttons}</SttvMenuButtonGroup>
  </aside>;
}

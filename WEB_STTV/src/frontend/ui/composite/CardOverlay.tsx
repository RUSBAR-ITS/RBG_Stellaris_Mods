import { useEffect, useId, useRef } from 'react';
import { createPortal } from 'react-dom';
import { SttvText } from '../base/Text';
import { SttvTechnologyDetails } from './TechnologyTooltipDetails';
import { sttvUseOverlay } from './useOverlay';
import './tooltip.css';

export interface CardAction {
  kind: 'menu' | 'details';
  id: string;
  anchor: HTMLAnchorElement;
}

export function CardOverlay({ action, enabled, close }: { action: CardAction; enabled?: string[]; close: () => void }) {
  const ref = useRef<HTMLDivElement>(null);
  const menuItem = useRef<HTMLAnchorElement>(null);
  const id = useId();
  const position = sttvUseOverlay(action.anchor, ref, true);
  useEffect(() => {
    const { anchor, kind } = action;
    anchor.setAttribute('aria-controls', id);
    if (kind === 'menu') menuItem.current?.focus({ preventScroll: true });
    function outside(event: PointerEvent) {
      if (event.target instanceof Node && !anchor.contains(event.target) && !ref.current?.contains(event.target)) close();
    }
    function keyboard(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        event.preventDefault();
        close();
        anchor.focus({ preventScroll: true });
      } else if (kind === 'details' && (event.key === 'PageDown' || event.key === 'PageUp') && ref.current) {
        event.preventDefault();
        ref.current.scrollTop += ref.current.clientHeight * (event.key === 'PageUp' ? -1 : 1);
      }
    }
    function wheel(event: WheelEvent) {
      if (!ref.current || ref.current.scrollHeight <= ref.current.clientHeight) return;
      event.preventDefault();
      const unit = event.deltaMode === 2 ? ref.current.clientHeight : event.deltaMode === 1 ? 16 : 1;
      ref.current.scrollTop += event.deltaY * unit;
    }
    anchor.addEventListener('wheel', wheel, { passive: false });
    document.addEventListener('pointerdown', outside, true);
    document.addEventListener('keydown', keyboard);
    return () => {
      anchor.removeAttribute('aria-controls');
      anchor.removeEventListener('wheel', wheel);
      document.removeEventListener('pointerdown', outside, true);
      document.removeEventListener('keydown', keyboard);
    };
  }, [action, close, id]);
  return createPortal(<div className="sttv-tooltip sttv-card-overlay" ref={ref} style={position} id={id}
    role={action.kind === 'menu' ? 'menu' : 'tooltip'}>{action.kind === 'menu'
      ? <a ref={menuItem} role="menuitem" href={action.anchor.href} onClick={close}><SttvText text={{ id: 'sttv_open_technology_page' }} /></a>
      : <SttvTechnologyDetails id={action.id} enabled={enabled} />}
  </div>, document.body);
}

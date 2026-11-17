import { useRef, useState, type KeyboardEvent, type PointerEvent } from 'react';
import config from '../../../../config/frontend/interface.json';
import { sttvUseLocalization } from '../../localization/context';
import './scrollbar.css';

interface SttvScrollbarProps {
  orientation: 'horizontal' | 'vertical'; content: number; viewport: number;
  offset: number; onChange: (offset: number) => void;
}
export function SttvScrollbar({ orientation, content, viewport, offset, onChange }: SttvScrollbarProps) {
  const track = useRef<HTMLDivElement>(null);
  const drag = useRef<{ pointer: number; offset: number } | null>(null);
  const [dragging, setDragging] = useState(false);
  const horizontal = orientation === 'horizontal';
  const maximum = Math.max(0, content - viewport);
  const size = Math.min(viewport, Math.max(config.minimumThumbSize, viewport * viewport / content));
  const travel = viewport - size;
  const position = maximum ? offset / maximum * travel : 0;
  const { text } = sttvUseLocalization();
  function change(next: number) { onChange(Math.max(0, Math.min(maximum, next))); }
  function coordinate(event: PointerEvent) { return horizontal ? event.clientX : event.clientY; }
  function key(event: KeyboardEvent) {
    const negative = horizontal ? 'ArrowLeft' : 'ArrowUp';
    const positive = horizontal ? 'ArrowRight' : 'ArrowDown';
    if (![negative, positive, 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    change(event.key === 'Home' ? 0 : event.key === 'End' ? maximum : offset + (event.key === negative ? -1 : 1) * config.scrollStep);
  }
  return <div ref={track} className="sttv-scrollbar" data-orientation={orientation} data-dragging={dragging}
    role="scrollbar" tabIndex={0} aria-label={text({ id: `sttv_${orientation}_scroll` })}
    aria-orientation={orientation} aria-valuemin={0} aria-valuemax={Math.round(maximum)} aria-valuenow={Math.round(offset)}
    aria-controls="sttv-viewport-content" onKeyDown={key} onPointerDown={event => {
      if (event.target !== event.currentTarget) return;
      const bounds = track.current!.getBoundingClientRect();
      const hit = coordinate(event) - (horizontal ? bounds.left : bounds.top);
      change(offset + (hit < position ? -viewport : viewport));
    }}>
    <div className="sttv-scrollbar-thumb" style={horizontal ? { width: size, left: position } : { height: size, top: position }}
      onPointerDown={event => { event.preventDefault(); event.stopPropagation(); track.current?.focus();
        drag.current = { pointer: coordinate(event), offset }; setDragging(true); event.currentTarget.setPointerCapture(event.pointerId); }}
      onPointerMove={event => { if (drag.current && travel > 0) change(drag.current.offset + (coordinate(event) - drag.current.pointer) * maximum / travel); }}
      onPointerUp={event => { drag.current = null; setDragging(false); event.currentTarget.releasePointerCapture(event.pointerId); }}
      onLostPointerCapture={() => { drag.current = null; setDragging(false); }} />
  </div>;
}

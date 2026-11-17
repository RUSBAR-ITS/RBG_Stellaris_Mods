import { useLayoutEffect, useRef, useState, type ReactNode } from 'react';
import config from '../../../../config/frontend/interface.json';
import { SttvScrollbar } from '../scroll/Scrollbar';
import './viewport.css';

export function SttvTechnologyViewport({ width, height, children }: { width: number; height: number; children: ReactNode }) {
  const container = useRef<HTMLDivElement>(null);
  const content = useRef<HTMLDivElement>(null);
  const [bounds, setBounds] = useState({ width: 0, height: 0 });
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const bar = config.scrollbarThickness;
  let horizontal = width > bounds.width, vertical = height > bounds.height;
  horizontal = width > bounds.width - (vertical ? bar : 0);
  vertical = height > bounds.height - (horizontal ? bar : 0);
  horizontal = width > bounds.width - (vertical ? bar : 0);
  const visibleWidth = Math.max(0, bounds.width - (vertical ? bar : 0));
  const visibleHeight = Math.max(0, bounds.height - (horizontal ? bar : 0));
  useLayoutEffect(() => {
    const element = content.current;
    if (!element) return;
    function wheel(event: WheelEvent) {
      if (!event.shiftKey || !element) return;
      event.preventDefault();
      const scale = event.deltaMode === 1 ? config.scrollStep : event.deltaMode === 2 ? element.clientWidth : 1;
      element.scrollLeft += (event.deltaY || event.deltaX) * scale;
    }
    element.addEventListener('wheel', wheel, { passive: false });
    return () => element.removeEventListener('wheel', wheel);
  }, []);
  useLayoutEffect(() => {
    const observer = new ResizeObserver(entries => {
      const rect = entries[0].contentRect;
      setBounds({ width: rect.width, height: rect.height });
    });
    if (container.current) observer.observe(container.current);
    return () => observer.disconnect();
  }, []);
  useLayoutEffect(() => {
    const element = content.current;
    if (!element) return;
    element.scrollLeft = Math.min(element.scrollLeft, Math.max(0, width - visibleWidth));
    element.scrollTop = Math.min(element.scrollTop, Math.max(0, height - visibleHeight));
    setOffset({ x: element.scrollLeft, y: element.scrollTop });
  }, [width, height, visibleWidth, visibleHeight]);
  return <div ref={container} className="sttv-viewport" style={{
    gridTemplateColumns: `minmax(0, 1fr) ${vertical ? bar : 0}px`,
    gridTemplateRows: `minmax(0, 1fr) ${horizontal ? bar : 0}px`,
  }}>
    <div id="sttv-viewport-content" ref={content} className="sttv-viewport-content"
      onScroll={event => setOffset({ x: event.currentTarget.scrollLeft, y: event.currentTarget.scrollTop })}>{children}</div>
    {vertical && <SttvScrollbar orientation="vertical" content={height} viewport={visibleHeight}
      offset={offset.y} onChange={next => { if (content.current) content.current.scrollTop = next; }} />}
    {horizontal && <SttvScrollbar orientation="horizontal" content={width} viewport={visibleWidth}
      offset={offset.x} onChange={next => { if (content.current) content.current.scrollLeft = next; }} />}
  </div>;
}

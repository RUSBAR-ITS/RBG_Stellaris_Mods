import { useEffect, useRef } from 'react';
import config from '../../../../config/frontend/interface.json';
import { createPortal } from 'react-dom';
import type { SttvTextRef } from '../../localization/model';
import { SttvText } from '../base/Text';
import { sttvUseOverlay } from './useOverlay';
import './tooltip.css';

export interface SttvTooltipContent { body: SttvTextRef; heading?: SttvTextRef }
export function SttvTooltip({ anchor, visible, content, id }:
  { anchor: HTMLElement | null; visible: boolean; content: SttvTooltipContent; id?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const position = sttvUseOverlay(anchor, ref, visible);
  useEffect(() => {
    if (!anchor || !visible) return;
    function wheel(event: WheelEvent) {
      const element = ref.current;
      if (!element || element.scrollHeight <= element.clientHeight) return;
      event.preventDefault(); event.stopPropagation();
      const scale = event.deltaMode === 1 ? config.scrollStep : event.deltaMode === 2 ? element.clientHeight : 1;
      element.scrollTop += event.deltaY * scale;
    }
    anchor.addEventListener('wheel', wheel, { passive: false });
    return () => anchor.removeEventListener('wheel', wheel);
  }, [anchor, visible]);
  if (!visible) return null;
  return createPortal(<div id={id} role="tooltip" className="sttv-tooltip" ref={ref} style={position}>
    {content.heading && <div className="sttv-tooltip-heading"><SttvText text={content.heading} role="tooltip-heading" /></div>}
    <SttvText text={content.body} role="tooltip-body" />
  </div>, document.body);
}

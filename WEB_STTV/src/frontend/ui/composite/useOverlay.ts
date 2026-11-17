import { useLayoutEffect, useState, type RefObject } from 'react';
import config from '../../../../config/frontend/interface.json';

export function sttvUseOverlay(anchor: HTMLElement | null, overlay: RefObject<HTMLElement | null>, open: boolean) {
  const [position, setPosition] = useState({ left: 0, top: 0 });
  useLayoutEffect(() => {
    if (!open || !anchor || !overlay.current) return;
    function update() {
      if (!anchor || !overlay.current) return;
      const bounds = anchor.getBoundingClientRect();
      const { width, height } = overlay.current.getBoundingClientRect();
      const margin = config.overlayMargin;
      let top = bounds.bottom + config.overlayGap;
      if (top + height > window.innerHeight - margin) top = bounds.top - height - config.overlayGap;
      setPosition({ left: Math.max(margin, Math.min(bounds.left, window.innerWidth - width - margin)),
        top: Math.max(margin, Math.min(top, window.innerHeight - height - margin)) });
    }
    update();
    const observer = new ResizeObserver(update);
    observer.observe(overlay.current);
    window.addEventListener('resize', update);
    window.addEventListener('scroll', update, true);
    return () => { observer.disconnect(); window.removeEventListener('resize', update);
      window.removeEventListener('scroll', update, true); };
  }, [anchor, overlay, open]);
  return position;
}

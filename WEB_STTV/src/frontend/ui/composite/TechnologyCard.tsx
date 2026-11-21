import type { SttvRepresentation, SttvCardTechnology } from '../../data/model';
import { sttvUseLocalization } from '../../localization/context';
import { SttvCardContent } from './CardContent';
import { useContext } from 'react';
import { technologyLink } from '../../app/technologyRoute';
import { TreeTooltipContext } from '../../app/tooltipCache';
import type { CardAction } from './CardOverlay';
import './technology-card.css';

export function SttvTechnologyCard({ technology, representation, onHover, onFocusChange, resourceIcon, open }:
  { technology: SttvCardTechnology; representation: SttvRepresentation; resourceIcon: string | null;
    open: (action: CardAction) => void; onHover: (active: boolean) => void; onFocusChange: (active: boolean) => void }) {
  const { language } = sttvUseLocalization();
  const { enabled } = useContext(TreeTooltipContext);
  function activate(anchor: HTMLAnchorElement, kind: CardAction['kind']) {
    open({ id: technology.id, anchor, kind });
  }
  return <a className="sttv-card" href={technologyLink(technology.id, language, enabled)} data-technology-id={technology.id}
    data-area={representation.area} data-event-only={technology.eventOnly}
    data-rarity={technology.dangerous ? 'dangerous' : technology.rare ? 'rare' : 'ordinary'}
    onFocus={() => onFocusChange(true)} onBlur={() => onFocusChange(false)}
    onMouseEnter={() => onHover(true)} onMouseLeave={() => onHover(false)}
    onClick={event => {
      if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault(); activate(event.currentTarget, 'details');
    }}
    onContextMenu={event => { event.preventDefault(); activate(event.currentTarget, 'menu'); }}
    onKeyDown={event => {
      if (event.key === ' ' || event.key === 'ContextMenu' || (event.shiftKey && event.key === 'F10')) {
        event.preventDefault(); activate(event.currentTarget, event.key === ' ' ? 'details' : 'menu');
      }
    }}>
    <SttvCardContent technology={technology} representation={representation} resourceIcon={resourceIcon} />
  </a>;
}

import { useId, useLayoutEffect, useRef, useState } from 'react';
import type { SttvRepresentation, SttvCardTechnology } from '../../data/model';
import { sttvUseLocalization } from '../../localization/context';
import { SttvCardContent } from './CardContent';
import { sttvTechnologyName } from '../../data/tree/comparison';
import { SttvTooltip } from './Tooltip';
import { SttvTechnologyTooltipDetails } from './TechnologyTooltipDetails';
import './technology-card.css';

export function SttvTechnologyCard({ technology, representation, onHover, resourceIcon, scale }:
  { technology: SttvCardTechnology; representation: SttvRepresentation; resourceIcon: string | null;
    scale: number; onHover: (active: boolean) => void }) {
  const ref = useRef<HTMLDivElement>(null);
  const [hover, setHover] = useState(false);
  const [focused, setFocused] = useState(false);
  useLayoutEffect(() => { setHover(false); setFocused(false); }, [scale]);
  const { text, language } = sttvUseLocalization();
  const tooltipId = useId();
  const name = sttvTechnologyName(technology, representation, text);
  return <div ref={ref} className="sttv-card" data-technology-id={technology.id}
    data-area={representation.area} data-rarity={technology.dangerous ? 'dangerous' : technology.rare ? 'rare' : 'ordinary'}
    tabIndex={0} onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
    aria-describedby={hover || focused ? tooltipId : undefined}
    onMouseEnter={() => { setHover(true); onHover(true); }} onMouseLeave={() => { setHover(false); onHover(false); }}>
    <SttvCardContent technology={technology} representation={representation} resourceIcon={resourceIcon} />
    <SttvTooltip id={tooltipId} anchor={ref.current} visible={hover || focused}
      content={{ heading: name, body: { source: 'database', id: representation.descriptionId } }}>
      {representation.id === 'base' && <SttvTechnologyTooltipDetails key={technology.id + ':' + language}
        technology={technology} language={language} />}
    </SttvTooltip>
  </div>;
}

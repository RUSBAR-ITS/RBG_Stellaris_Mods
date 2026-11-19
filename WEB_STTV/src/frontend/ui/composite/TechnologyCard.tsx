import { useId, useRef, useState } from 'react';
import type { SttvRepresentation, SttvTechnology } from '../../data/model';
import { sttvUseLocalization } from '../../localization/context';
import { SttvText } from '../base/Text';
import { sttvTechnologyName } from '../../data/tree/comparison';
import { SttvTooltip } from './Tooltip';
import './technology-card.css';

export function SttvTechnologyCard({ technology, representation }:
  { technology: SttvTechnology; representation: SttvRepresentation }) {
  const ref = useRef<HTMLDivElement>(null);
  const [hover, setHover] = useState(false);
  const [focused, setFocused] = useState(false);
  const { text } = sttvUseLocalization();
  const tooltipId = useId();
  const name = sttvTechnologyName(technology, representation, text);
  const label = <SttvText text={name} role="card" className="sttv-card-title" />;
  return <div ref={ref} className="sttv-card" data-technology-id={technology.id}
    tabIndex={0} onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
    aria-describedby={hover || focused ? tooltipId : undefined}
    onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}>
    <div className="sttv-card-content">{label}</div>
    <SttvTooltip id={tooltipId} anchor={ref.current} visible={hover || focused}
      content={{ heading: name, body: { source: 'database', id: representation.descriptionId } }} />
  </div>;
}

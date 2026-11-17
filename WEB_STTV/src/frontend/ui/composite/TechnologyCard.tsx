import { useId, useRef, useState } from 'react';
import type { SttvRepresentation, SttvTechnology } from '../../data/model';
import { sttvUseLocalization } from '../../localization/context';
import { SttvText } from '../base/Text';
import { SttvSelect } from '../base/Select';
import { SttvTooltip } from './Tooltip';
import './technology-card.css';

export function SttvTechnologyCard({ technology, representation, onSelect }:
  { technology: SttvTechnology; representation: SttvRepresentation; onSelect: (value: string) => void }) {
  const ref = useRef<HTMLDivElement>(null);
  const [hover, setHover] = useState(false);
  const [open, setOpen] = useState(false);
  const { text } = sttvUseLocalization();
  const tooltipId = useId();
  const name = { source: 'database' as const, id: representation.nameId };
  const titles = technology.representations.map(item => text({ source: 'database', id: item.nameId }));
  const options = technology.representations.map((item, index) => ({ value: item.id,
    label: { source: 'database' as const, id: item.nameId,
      ...(item.variantNumber !== undefined && titles.filter(title => title === titles[index]).length > 1
        ? { suffix: { id: 'sttv_variant_suffix', params: { number: item.variantNumber } } } : {}) } }));
  const label = <SttvText text={name} role="card" className="sttv-card-title" />;
  return <div ref={ref} className="sttv-card" data-technology-id={technology.id}
    aria-describedby={hover && !open ? tooltipId : undefined}
    onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}>
    {options.length > 1 ? <SttvSelect className="sttv-card-trigger" options={options}
      value={representation.id} onChange={onSelect} onOpenChange={setOpen}>{label}</SttvSelect>
      : <div className="sttv-card-content">{label}</div>}
    <SttvTooltip id={tooltipId} anchor={ref.current} visible={hover && !open}
      content={{ heading: name, body: { source: 'database', id: representation.descriptionId } }} />
  </div>;
}

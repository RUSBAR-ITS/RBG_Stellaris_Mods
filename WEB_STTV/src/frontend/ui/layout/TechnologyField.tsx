import { useMemo } from 'react';
import type { SttvCatalog, SttvTechnology } from '../../data/model';
import { sttvLayout, sttvRepresentation, type SttvAreaLayout, type SttvColumn } from '../../data/layout';
import { SttvText } from '../base/Text';
import { SttvTechnologyCard } from '../composite/TechnologyCard';
import { SttvTechnologyViewport } from './TechnologyViewport';
import './field.css';

interface SttvFieldProps {
  data: SttvCatalog;
  selected: Record<string, string>;
  onSelect: (id: string, value: string) => void;
}
function SttvTierColumn({ column, technologies, selected, onSelect }:
  Omit<SttvFieldProps, 'data'> & { column: SttvColumn; technologies: Record<string, SttvTechnology> }) {
  return <section className="sttv-tier-column" data-tier={column.tier}>
    <h3 className="sttv-tier-heading"><SttvText role="tier" text={{ id: 'sttv_tier', params: { number: column.tier } }} /></h3>
    <div className="sttv-tier-cards">{column.ids.map(id => <SttvTechnologyCard key={id}
      technology={technologies[id]} representation={sttvRepresentation(technologies[id], selected)}
      onSelect={value => onSelect(id, value)} />)}</div>
  </section>;
}
function SttvResearchArea({ area, data, selected, onSelect }: SttvFieldProps & { area: SttvAreaLayout }) {
  return <section className="sttv-research-area" data-area={area.area} style={{ height: area.height }}>
    <h2 className="sttv-area-heading"><SttvText role="area" text={{ id: `sttv_${area.area}` }} /></h2>
    <div className="sttv-columns">{area.columns.map(column => <SttvTierColumn key={column.tier}
      column={column} technologies={data.technologies} selected={selected} onSelect={onSelect} />)}</div>
  </section>;
}
export function SttvTechnologyField(props: SttvFieldProps) {
  const layout = useMemo(() => sttvLayout(props.data.technologies, props.selected), [props.data, props.selected]);
  function select(id: string, value: string) {
    props.onSelect(id, value);
    requestAnimationFrame(() => document.querySelector<HTMLButtonElement>(
      `[data-technology-id="${CSS.escape(id)}"] button`)?.focus({ preventScroll: true }));
  }
  return <SttvTechnologyViewport width={layout.width} height={layout.height}>
    <div className="sttv-technology-field" style={{ width: layout.width, height: layout.height }}>
      {layout.areas.map(area => <SttvResearchArea key={area.area} {...props} area={area} onSelect={select} />)}
    </div>
  </SttvTechnologyViewport>;
}

import type { SttvRepresentation, SttvCardTechnology } from '../../data/model';
import { sttvUseLocalization } from '../../localization/context';
import { sttvTechnologyName } from '../../data/tree/comparison';
import { SttvResourceImage } from '../base/ResourceImage';
import { SttvText } from '../base/Text';
import type { ReactNode } from 'react';

export function SttvAttributeRow({ label, children }: { label: string; children: ReactNode }) {
  return <div className="sttv-card-attribute"><SttvText text={{ id: label }} /> {children}</div>;
}

export function SttvCardContent({ technology: tech, representation: rep, resourceIcon, measuring = false }:
  { technology: SttvCardTechnology; representation: SttvRepresentation; resourceIcon: string | null; measuring?: boolean }) {
  const { text, language } = sttvUseLocalization();
  const number = new Intl.NumberFormat(language, { maximumFractionDigits: 10 });
  const information = [rep.categories.map(id => text({ source: 'database', id })).join(text({ id: 'sttv_category_separator' })),
    text({ id: 'sttv_card_level', params: { number: tech.tier } }), tech.startTech ? text({ id: 'sttv_card_starting' }) : ''].filter(Boolean);
  return <div className="sttv-card-content">
    <SttvResourceImage id={rep.iconAssetId} className="sttv-card-image" measuring={measuring} />
    <div className="sttv-card-details">
      <SttvText text={sttvTechnologyName(tech, rep, text)} role="card" className="sttv-card-title" />
      <div className="sttv-card-information">{information.join(text({ id: 'sttv_card_separator' }))}</div>
      {tech.cost !== null && <SttvAttributeRow label="sttv_card_cost">
        <SttvResourceImage id={resourceIcon} label={text({ id: `sttv_${rep.area}` })} className="sttv-cost-image" measuring={measuring} />
        <span>{number.format(tech.cost)}</span>
      </SttvAttributeRow>}
      {tech.weight !== null && <SttvAttributeRow label="sttv_card_weight">{number.format(tech.weight)}</SttvAttributeRow>}
      {tech.levels !== null && tech.levels > 1 && <SttvAttributeRow label="sttv_card_levels">{number.format(tech.levels)}</SttvAttributeRow>}
    </div>
  </div>;
}

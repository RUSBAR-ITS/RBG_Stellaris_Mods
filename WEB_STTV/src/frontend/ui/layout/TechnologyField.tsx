import type { SttvCatalog } from '../../data/model';
import type { SttvLayout } from '../../data/tree/model';
import { sttvRepresentation } from '../../data/tree/comparison';
import { SttvText } from '../base/Text';
import { SttvTechnologyCard } from '../composite/TechnologyCard';
import { SttvTechnologyViewport } from './TechnologyViewport';
import './field.css';

export function SttvTechnologyField({ data, layout }: { data: SttvCatalog; layout: SttvLayout }) {
  const columns = `repeat(${layout.tiers.length}, var(--sttv-card-width))`;
  return <SttvTechnologyViewport width={layout.width} height={layout.height}>
    <div className="sttv-technology-field" style={{ width: layout.width, height: layout.height }}>
      {layout.areas.map(area => <section key={area.area} className="sttv-research-area" data-area={area.area}
        style={{ height: area.height }}>
        <h2 className="sttv-area-heading"><SttvText role="area" text={{ id: `sttv_${area.area}` }} /></h2>
        <div className="sttv-tier-headings" style={{ gridTemplateColumns: columns }}>
          {layout.tiers.map(tier => <h3 key={tier} className="sttv-tier-heading">
            <SttvText role="tier" text={{ id: 'sttv_tier', params: { number: tier } }} />
          </h3>)}
        </div>
        <div className="sttv-tree-grid" style={{ gridTemplateColumns: columns,
          gridTemplateRows: area.rowCount ? `repeat(${area.rowCount}, var(--sttv-card-height))` : undefined }}>
          {area.cards.map(card => <div key={card.id} data-tier={card.column} data-row={card.row}
            style={{ gridColumn: card.column + 1, gridRow: card.row + 1 }}>
            <SttvTechnologyCard technology={data.technologies[card.id]}
              representation={sttvRepresentation(data.technologies[card.id], data.treeCombination.parameters.variants)} />
          </div>)}
        </div>
      </section>)}
    </div>
  </SttvTechnologyViewport>;
}

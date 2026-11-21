import type { SttvCardCatalog } from '../../data/model';
import { useCallback, useContext, useLayoutEffect, useState } from 'react';
import type { SttvLayout } from '../../data/tree/model';
import { sttvRepresentation } from '../../data/tree/comparison';
import { SttvText } from '../base/Text';
import { SttvTechnologyCard } from '../composite/TechnologyCard';
import { SttvTechnologyViewport } from './TechnologyViewport';
import { SttvConnections } from './Connections';
import { CardOverlay, type CardAction } from '../composite/CardOverlay';
import { TreeTooltipContext } from '../../app/tooltipCache';
import './field.css';

type FieldLayout = Pick<SttvLayout, 'areas' | 'tiers' | 'columns' | 'height' | 'width'>;
export function SttvTechnologyField({ data, layout, scale }: { data: SttvCardCatalog; layout: FieldLayout; scale: number }) {
  const [hover, setHover] = useState<{ layout: FieldLayout; scale: number; id: string } | null>(null);
  const [focused, setFocused] = useState<string | null>(null);
  const { enabled, active } = useContext(TreeTooltipContext);
  const [action, setAction] = useState<CardAction | null>(null);
  const close = useCallback(() => setAction(null), []);
  function open(next: CardAction) {
    setAction(previous => next.kind === 'details' && previous?.kind === 'details' && previous.id === next.id ? null : next);
  }
  useLayoutEffect(() => { close(); setHover(null); setFocused(null); }, [scale, active, layout, close]);
  const hovered = hover?.layout === layout && hover.scale === scale ? hover.id : null;
  return <SttvTechnologyViewport width={layout.width} height={layout.height} scale={scale}>
    <div className="sttv-technology-field" style={{ width: layout.width, height: layout.height }}>
      {layout.areas.map(area => <section key={area.area} className="sttv-research-area" data-area={area.area}
        style={{ height: area.height }}>
        <h2 className="sttv-area-heading" style={{ paddingLeft: layout.columns[0] }}><SttvText role="area" text={{ id: `sttv_${area.area}` }} /></h2>
        <div className="sttv-tier-headings">
          {layout.tiers.map(tier => <h3 key={tier} className="sttv-tier-heading" style={{ left: layout.columns[tier] }}>
            <SttvText role="tier" text={{ id: 'sttv_tier', params: { number: tier } }} />
          </h3>)}
        </div>
        <div className="sttv-tree-grid" style={{ height: area.geometry.height }}>
          <SttvConnections geometry={area.geometry} hovered={hovered ?? focused} width={layout.width} />
          {area.cards.map(card => <div key={card.id} className="sttv-positioned-card" data-tier={card.column} data-row={card.row}
            style={{ left: area.geometry.cards[card.id].x, top: area.geometry.cards[card.id].y,
              '--sttv-card-height': `${area.geometry.cards[card.id].height}px` } as import('react').CSSProperties}>
            <SttvTechnologyCard technology={data.technologies[card.id]} open={open}
              onHover={active => setHover(active ? { layout, scale, id: card.id } : null)}
              onFocusChange={active => setFocused(active ? card.id : null)}
              resourceIcon={data.presentation?.research_icons[sttvRepresentation(data.technologies[card.id], data.treeCombination.parameters.variants).area] ?? null}
              representation={sttvRepresentation(data.technologies[card.id], data.treeCombination.parameters.variants)} />
          </div>)}
        </div>
      </section>)}
    </div>
    {active && action && <CardOverlay key={action.id + action.kind} action={action} enabled={enabled} close={close} />}
  </SttvTechnologyViewport>;
}

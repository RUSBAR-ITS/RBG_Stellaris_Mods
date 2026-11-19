import { useLayoutEffect, useRef } from 'react';
import type { SttvCatalog } from '../../data/model';
import { sttvRepresentation } from '../../data/tree/comparison';
import { SttvCardContent } from './CardContent';
import dimensions from '../../../../config/frontend/interface.json';
import { sttvUseLocalization } from '../../localization/context';

export function SttvCardMeasurement({ data, onMeasure }: { data: SttvCatalog; onMeasure: (height: number) => void }) {
  const root = useRef<HTMLDivElement>(null);
  const { language } = sttvUseLocalization();
  useLayoutEffect(() => {
    let active = true;
    void document.fonts.ready.then(() => {
      if (!active || !root.current) return;
      const heights = [...root.current.querySelectorAll<HTMLElement>('.sttv-card')].map(card => card.getBoundingClientRect().height);
      onMeasure(Math.max(dimensions.cardHeight, Math.ceil(Math.max(0, ...heights))));
    });
    return () => { active = false; };
  }, [data, language, onMeasure]);
  return <div ref={root} className="sttv-card-measurement" aria-hidden="true">
    {Object.values(data.technologies).map(tech => {
      const rep = sttvRepresentation(tech, data.treeCombination.parameters.variants);
      return <div key={tech.id} className="sttv-card" data-area={rep.area}>
        <SttvCardContent technology={tech} representation={rep} measuring
          resourceIcon={data.presentation?.research_icons[rep.area] ?? null} />
      </div>;
    })}
  </div>;
}

import { useEffect, useState } from 'react';
import { request } from '../../app/reference';
import type { SttvCardTechnology } from '../../data/model';
import type { SttvLanguage } from '../../localization/model';
import { SttvText } from '../base/Text';

interface Expression {
  kind: string;
  text?: string;
  children?: Expression[];
  formula?: Expression[];
  expression?: unknown;
}
type Sections = Partial<Record<'prerequisites' | 'potential' | 'allow' | 'weight_modifier', Expression[]>>;
interface Response { technology_id: string; language: SttvLanguage; sections: Sections }

// A new tree supplies new card objects, so its tooltips cannot reuse an older snapshot.
const cache = new WeakMap<SttvCardTechnology, Partial<Record<SttvLanguage, Sections>>>();

function Expressions({ items }: { items?: Expression[] }) {
  if (!items?.length) return null;
  return <ul>{items.map((node, index) => <li key={index}>
    {node.text}
    {node.kind === 'unrecognized' && <code>{JSON.stringify(node.expression)}</code>}
    <Expressions items={node.children} />
    <Expressions items={node.formula} />
  </li>)}</ul>;
}

function Heading({ id }: { id: string }) {
  return <h3><SttvText text={{ id }} role="tooltip-heading" /></h3>;
}

export function SttvTechnologyTooltipDetails({ technology, language }:
  { technology: SttvCardTechnology; language: SttvLanguage }) {
  const [sections, setSections] = useState<Sections | undefined>(() => cache.get(technology)?.[language]);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    const cached = cache.get(technology)?.[language];
    setFailed(false);
    setSections(cached);
    if (cached) return;
    const controller = new AbortController();
    request<Response>('/api/trees/technology-tooltip', 'POST', { technology_id: technology.id, language }, controller.signal)
      .then(result => {
        if (controller.signal.aborted) return;
        if (result.technology_id !== technology.id || result.language !== language || !result.sections) {
          throw new Error('Unexpected technology tooltip response');
        }
        cache.set(technology, { ...cache.get(technology), [language]: result.sections });
        setSections(result.sections);
      })
      .catch(() => { if (!controller.signal.aborted) setFailed(true); });
    return () => controller.abort();
  }, [technology, language]);
  if (!sections) return <div className="sttv-tooltip-status" role="status">
    <SttvText text={{ id: failed ? 'sttv_tooltip_error' : 'sttv_tooltip_loading' }} role="tooltip-body" />
  </div>;
  const { prerequisites, potential, allow, weight_modifier: weights } = sections;
  return <div className="sttv-tooltip-details">
    {!!prerequisites?.length && <section><Heading id="sttv_tooltip_prerequisites" /><Expressions items={prerequisites} /></section>}
    {(!!potential?.length || !!allow?.length) && <section><Heading id="sttv_tooltip_availability" />
      {!!potential?.length && <><h4><SttvText text={{ id: 'sttv_tooltip_potential' }} role="tooltip-body" /></h4>
        <Expressions items={potential} /></>}
      {!!allow?.length && <><h4><SttvText text={{ id: 'sttv_tooltip_allow' }} role="tooltip-body" /></h4>
        <Expressions items={allow} /></>}
    </section>}
    {!!weights?.length && <section><Heading id="sttv_tooltip_weight" /><Expressions items={weights} /></section>}
  </div>;
}

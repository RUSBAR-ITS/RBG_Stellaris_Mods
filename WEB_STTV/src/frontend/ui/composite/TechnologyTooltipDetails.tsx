import { useEffect, useState } from 'react';
import { request } from '../../app/reference';
import type { SttvCardTechnology } from '../../data/model';
import type { SttvLanguage } from '../../localization/model';
import { SttvText } from '../base/Text';
import { SttvGameText } from '../base/GameText';

interface Expression {
  kind: string;
  key?: string;
  text?: string;
  children?: Expression[];
  formula?: Expression[];
  expression?: unknown;
  operations?: Expression[];
  condition?: Expression;
}
type Sections = Partial<Record<'prerequisites' | 'potential' | 'allow' | 'weight_modifier', Expression[]>>;
interface Response { technology_id: string; language: SttvLanguage; sections: Sections }

// A new tree supplies new card objects, so its tooltips cannot reuse an older snapshot.
const cache = new WeakMap<SttvCardTechnology, Partial<Record<SttvLanguage, Sections>>>();

function Expressions({ items }: { items?: Expression[] }) {
  if (!items?.length) return null;
  return <ul>{items.map((node, index) => <li key={index}><ExpressionLine node={node} /></li>)}</ul>;
}

function ExpressionLine({ node }: { node: Expression }) {
  if (node.kind === 'unrecognized') return <code>{JSON.stringify(node.expression)}</code>;
  const children = node.children;
  const child = children?.length === 1 ? children[0] : undefined;
  const inlineScope = node.kind === 'scope' && child?.kind === 'condition' && !child.children?.length;
  let text = node.text ?? '';
  if (children?.length && text && !inlineScope) text = text.trimEnd().replace(/:+$/, '') + ':';
  return <><SttvGameText value={text} />
    {inlineScope ? <> — <ExpressionLine node={child} /></> : <Expressions items={children} />}
    <Expressions items={node.formula} />
  </>;
}

function WeightRules({ items }: { items: Expression[] }) {
  return <ul>{items.map((rule, index) => <li key={index}>
    {rule.kind === 'modifier' && rule.operations ? <>
      {rule.operations.map((op, i) => <strong key={i}>({op.key === 'add' && op.formula ? '+' : ''}<SttvGameText value={op.text ?? ''} />) </strong>)}
      {rule.condition && <ExpressionLine node={rule.condition} />}
      {rule.operations.map((op, i) => op.formula?.length ? <div key={i}>
        <SttvText text={{ id: 'sttv_tooltip_formula' }} role="tooltip-body" />
        {rule.operations!.length > 1 && <> (<SttvGameText value={op.text ?? ''} />)</>}
        <Expressions items={op.formula} />
      </div> : null)}
    </> : <ExpressionLine node={rule} />}
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
    {!!weights?.length && <section><Heading id="sttv_tooltip_weight" /><WeightRules items={weights} /></section>}
  </div>;
}

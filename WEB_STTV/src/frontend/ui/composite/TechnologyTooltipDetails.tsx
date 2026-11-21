import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { technologyLink } from '../../app/technologyRoute';
import { request } from '../../app/reference';
import { sttvUseLocalization } from '../../localization/context';
import { SttvText } from '../base/Text';
import { SttvGameText } from '../base/GameText';
import { TreeTooltipContext, type Expression, type TechnologyResponse } from '../../app/tooltipCache';

const EnabledDlc = createContext<string[] | undefined>(undefined);

function Expressions({ items }: { items?: Expression[] }) {
  if (!items?.length) return null;
  return <ul>{items.map((node, index) => <li key={index}><ExpressionLine node={node} /></li>)}</ul>;
}

function RewardDetails({ summary, items }: { summary: ReactNode; items?: Expression[] }) {
  const [expanded, setExpanded] = useState(false);
  return <details className="sttv-reward-details" onToggle={event => setExpanded(event.currentTarget.open)}>
    <summary>{summary}</summary>
    {expanded && <Expressions items={items} />}
  </details>;
}

function ExpressionLine({ node }: { node: Expression }) {
  const { language } = sttvUseLocalization();
  const enabled = useContext(EnabledDlc);
  const evidence = node.expression ?? node.evidence;
  const children = node.children;
  const child = children?.length === 1 ? children[0] : undefined;
  const inlineScope = node.kind === 'scope' && child?.kind === 'condition' && !child.children?.length;
  let text = node.text ?? '';
  if (children?.length && text && !inlineScope) text = text.trimEnd().replace(/:+$/, '') + ':';
  const heading = <span className={node.source?.[0] === 'events' ? 'sttv-event-name' : undefined}><SttvGameText value={node.source?.[0] === 'events' ? text.replace(/§[\w!]/gu, '') : text} /></span>;
  if (node.summary?.length) return <RewardDetails items={children} summary={<>{heading}{' '}
    {node.summary.map((part, i) => <span key={i}>{i > 0 && ' · '}<SttvGameText value={part} /></span>)}
  </>} />;
  return <>{node.technology_link ? <a href={technologyLink(node.technology_link, language, enabled)}>{heading}</a> : heading}
    {inlineScope ? <> — <ExpressionLine node={child} /></> : <Expressions items={children} />}
    {evidence != null && <details><summary><SttvText text={{ id: 'sttv_condition_details' }} role="tooltip-body" /></summary>
      <code>{JSON.stringify(evidence)}</code></details>}
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

export function SttvTechnologyDetails({ id, enabled, page = false }:
  { id: string; enabled?: string[]; page?: boolean }) {
  const { language } = sttvUseLocalization();
  const { cache } = useContext(TreeTooltipContext);
  const key = JSON.stringify([id, language, enabled ?? null]);
  const [state, setState] = useState<{ key: string; error?: string; result?: TechnologyResponse }>();
  const result = cache.get(key) ?? (state?.key === key ? state.result : undefined);
  useEffect(() => {
    if (cache.has(key)) return;
    const generation = cache.generation;
    const controller = new AbortController();
    request<TechnologyResponse>('/api/trees/technology-tooltip', 'POST',
      { technology_id: id, language, enabled_dlc: enabled }, controller.signal).then(value => {
        if (controller.signal.aborted) return;
        if (cache.generation !== generation) {
          setState({ key, error: 'tooltip_reset' });
          return;
        }
        if (value.technology_id !== id || value.language !== language || !value.sections)
          throw new Error('Unexpected technology response');
        cache.set(key, value);
        setState({ key, result: value });
      }).catch((err: Error) => {
        if (!controller.signal.aborted) setState({ key, error: err.message });
      });
    return () => controller.abort();
  }, [cache, key, id, language, enabled]);
  if (!result) {
    const error = state?.key === key ? state.error : undefined;
    const status = error === 'tooltip_reset' ? 'sttv_reset_done_tooltips'
      : error === 'technology_not_found' ? 'sttv_unknown_technology'
      : error ? 'sttv_technology_request_error' : 'sttv_tooltip_loading';
    return <div role="status" className="sttv-tooltip-status"><SttvText text={{
      id: status,
      params: { id } }} /></div>;
  }
  const { sections } = result;
  const { prerequisites, potential, allow, weight_modifier: weights } = sections;
  const Title = page ? 'h1' : 'h2';
  return <EnabledDlc.Provider value={enabled}><div className="sttv-tooltip-details">
    <Title className="sttv-tooltip-heading"><SttvGameText value={result.name} /></Title>
    {result.description && <p><SttvGameText value={result.description} /></p>}
    {!!prerequisites?.length && <section><Heading id="sttv_tooltip_prerequisites" /><Expressions items={prerequisites} /></section>}
    {(!!potential?.length || !!allow?.length || !!sections.starting_potential?.length) && <section><Heading id="sttv_tooltip_availability" />
      {!!potential?.length && <><h4><SttvText text={{ id: 'sttv_tooltip_potential' }} role="tooltip-body" /></h4>
        <Expressions items={potential} /></>}
      {!!allow?.length && <><h4><SttvText text={{ id: 'sttv_tooltip_allow' }} role="tooltip-body" /></h4>
        <Expressions items={allow} /></>}
      {!!sections.starting_potential?.length && <><h4><SttvText text={{ id: 'sttv_tooltip_starting' }} role="tooltip-body" /></h4>
        <Expressions items={sections.starting_potential} /></>}
    </section>}
    {(!!weights?.length || !!sections.weight_notes?.length) && <section><Heading id="sttv_tooltip_weight" />
      <Expressions items={sections.weight_notes} />{weights?.length ? <WeightRules items={weights} /> : null}</section>}
    {!!sections.research_options?.length && <section><Heading id="sttv_tooltip_options" /><Expressions items={sections.research_options} /></section>}
    {!!sections.researched_grants?.length && <section><Heading id="sttv_tooltip_grants" /><Expressions items={sections.researched_grants} /></section>}
    {!!sections.research_progress?.length && <section><Heading id="sttv_tooltip_progress" />
      <Expressions items={sections.research_progress} /></section>}
  </div></EnabledDlc.Provider>;
}

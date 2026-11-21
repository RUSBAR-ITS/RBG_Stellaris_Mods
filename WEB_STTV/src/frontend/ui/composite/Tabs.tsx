import { useId, type KeyboardEvent, type ReactNode } from 'react';
import { sttvUseLocalization } from '../../localization/context';
import './tabs.css';

interface Tab<T extends string> { id: T; label: string; content: ReactNode }

export function SttvTabs<T extends string>({ label, tabs, selected, onSelect }: {
  label: string; tabs: Tab<T>[]; selected: T; onSelect: (id: T) => void;
}) {
  const group = useId();
  const { text } = sttvUseLocalization();
  function navigate(event: KeyboardEvent<HTMLButtonElement>, index: number) {
    const last = tabs.length - 1;
    const keys: Record<string, number> = { ArrowRight: (index + 1) % tabs.length, ArrowLeft: (index + last) % tabs.length,
      Home: 0, End: last };
    const target = keys[event.key];
    if (target === undefined) return;
    event.preventDefault();
    onSelect(tabs[target].id);
    document.getElementById(group + tabs[target].id)?.focus();
  }
  return <div className="sttv-tabs">
    <div role="tablist" aria-label={text({ id: label })}>
      {tabs.map((tab, i) => <button key={tab.id} type="button" role="tab" id={group + tab.id}
        aria-controls={group + '-panel-' + tab.id} aria-selected={tab.id === selected} tabIndex={tab.id === selected ? 0 : -1}
        onClick={() => onSelect(tab.id)} onKeyDown={event => navigate(event, i)}>{text({ id: tab.label })}</button>)}
    </div>
    {tabs.map(tab => <section key={tab.id} role="tabpanel" id={group + '-panel-' + tab.id}
      aria-labelledby={group + tab.id} hidden={tab.id !== selected}>{tab.id === selected && tab.content}</section>)}
  </div>;
}

import { useEffect, useId, useRef, useState, type ReactNode, type KeyboardEvent } from 'react';
import { createPortal } from 'react-dom';
import type { SttvTextRef } from '../../localization/model';
import { sttvUseLocalization } from '../../localization/context';
import { SttvText } from './Text';
import { SttvIcon } from './Icon';
import { sttvUseOverlay } from '../composite/useOverlay';
import './select.css';

export interface SttvOption { value: string; label: SttvTextRef }
interface SttvSelectProps {
  options: SttvOption[]; value: string; onChange: (value: string) => void;
  accessibleName?: SttvTextRef; className?: string;
  children?: ReactNode; onOpenChange?: (open: boolean) => void;
}
export function SttvSelect({ options, value, onChange, accessibleName, className = '', children, onOpenChange }: SttvSelectProps) {
  const trigger = useRef<HTMLButtonElement>(null);
  const list = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const { text } = sttvUseLocalization();
  const listId = useId();
  const selected = options.find(option => option.value === value);
  const position = sttvUseOverlay(trigger.current, list, open);
  function close(restore = false) {
    setOpen(false); onOpenChange?.(false);
    if (restore) trigger.current?.focus();
  }
  function show() {
    if (!options.length) return;
    setActive(Math.max(0, options.findIndex(option => option.value === value)));
    setOpen(true); onOpenChange?.(true);
  }
  function choose(index: number) { close(true); onChange(options[index].value); }
  useEffect(() => {
    if (!open) return;
    list.current?.focus();
    function outside(event: PointerEvent) {
      if (!trigger.current?.contains(event.target as Node) && !list.current?.contains(event.target as Node)) close();
    }
    document.addEventListener('pointerdown', outside);
    return () => document.removeEventListener('pointerdown', outside);
  }, [open]);
  useEffect(() => { list.current?.querySelector(`[data-index="${active}"]`)?.scrollIntoView({ block: 'nearest' }); }, [active, open]);
  function navigate(event: KeyboardEvent) {
    if (event.key === 'Escape') { event.preventDefault(); close(true); }
    else if (event.key === 'Tab') close(true);
    else if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault(); setActive(index => (index + (event.key === 'ArrowDown' ? 1 : -1) + options.length) % options.length);
    } else if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); choose(active); }
    else if (event.key === 'Home' || event.key === 'End') {
      event.preventDefault(); setActive(event.key === 'Home' ? 0 : options.length - 1);
    }
  }
  return <>
    <button ref={trigger} type="button" className={`sttv-select-trigger ${className}`} aria-haspopup="listbox"
      aria-expanded={open} aria-controls={open ? listId : undefined}
      aria-label={accessibleName ? text(accessibleName) : selected ? text(selected.label) : undefined}
      onClick={() => open ? close() : show()} onKeyDown={event => {
        if (event.key === 'ArrowDown') { event.preventDefault(); show(); }
      }}>
      {children ?? <><SttvText text={selected?.label ?? { id: value }} role="select" /><SttvIcon name="down" /></>}
    </button>
    {open && createPortal(<div id={listId} role="listbox" tabIndex={-1} ref={list}
      aria-label={accessibleName ? text(accessibleName) : selected && text(selected.label)}
      aria-activedescendant={`${listId}-${active}`} className="sttv-select-list"
      style={{ ...position, minWidth: trigger.current?.offsetWidth }} onKeyDown={navigate}>
      {options.map((option, index) => <div id={`${listId}-${index}`} key={option.value} role="option"
        aria-selected={option.value === value} data-active={index === active} data-index={index}
        className="sttv-select-option" onMouseEnter={() => setActive(index)} onClick={() => choose(index)}>
        <span className="sttv-select-marker">{option.value === value && <SttvIcon name="check" />}</span>
        <SttvText text={option.label} role="select" />
      </div>)}
    </div>, document.body)}
  </>;
}

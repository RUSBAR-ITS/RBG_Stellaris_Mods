import { useId, useRef, useState } from 'react';
import type { SttvTextRef } from '../../localization/model';
import type { SttvIconName } from '../../assets/icons';
import { sttvUseLocalization } from '../../localization/context';
import { SttvTooltip, type SttvTooltipContent } from '../composite/Tooltip';
import { SttvText } from './Text';
import { SttvIcon } from './Icon';
import './controls.css';

interface SttvButtonProps {
  label?: SttvTextRef;
  icon?: SttvIconName;
  accessibleName?: SttvTextRef;
  tooltip?: SttvTooltipContent;
  onClick: () => void;
  border?: 'always' | 'hover' | 'never';
  className?: string;
  disabled?: boolean;
  current?: boolean;
}
export function SttvButton({ label, icon, accessibleName = label, tooltip, onClick,
  border = 'always', className = '', disabled = false, current }: SttvButtonProps) {
  const ref = useRef<HTMLButtonElement>(null);
  const [hover, setHover] = useState(false);
  const [focus, setFocus] = useState(false);
  const { text } = sttvUseLocalization();
  const tooltipId = useId();
  return <>
    <button ref={ref} type="button" className={`sttv-button ${className}`} data-border={border}
      disabled={disabled} aria-current={current ? 'page' : undefined}
      aria-label={accessibleName && text(accessibleName)} aria-describedby={tooltip && (hover || focus) ? tooltipId : undefined}
      onClick={onClick} onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      onFocus={event => setFocus(event.currentTarget.matches(':focus-visible'))}
      onPointerDown={() => setFocus(false)} onKeyDown={() => setFocus(true)} onBlur={() => setFocus(false)}>
      {icon && <SttvIcon name={icon} />}{label && <SttvText text={label} role="button" />}
    </button>
    {tooltip && <SttvTooltip id={tooltipId} anchor={ref.current} visible={hover || focus} content={tooltip} />}
  </>;
}

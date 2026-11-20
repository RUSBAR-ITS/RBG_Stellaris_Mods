import type { SttvTextRef } from '../../localization/model';
import { sttvUseLocalization } from '../../localization/context';
import { SttvText } from './Text';
import './switch.css';

export function SttvSwitch({ label, checked, disabled, onChange }: {
  label: SttvTextRef; checked: boolean; disabled?: boolean; onChange: () => void;
}) {
  const { text } = sttvUseLocalization();
  return <button type="button" role="switch" className="sttv-switch" aria-label={text(label)}
    aria-checked={checked} disabled={disabled} onClick={onChange}>
    <span className="sttv-switch-track" aria-hidden="true"><span className="sttv-switch-thumb" /></span>
    <SttvText text={{ id: checked ? 'sttv_dlc_enabled' : 'sttv_dlc_disabled' }} />
  </button>;
}

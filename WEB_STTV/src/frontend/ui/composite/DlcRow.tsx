import type { SttvTextRef } from '../../localization/model';
import { SttvResourceImage } from '../base/ResourceImage';
import { SttvText } from '../base/Text';
import { SttvSwitch } from '../base/Switch';

export function SttvDlcRow({ id, name, image, checked, disabled, onChange }: {
  id: string; name: SttvTextRef; image: string | null; checked: boolean; disabled: boolean; onChange: () => void;
}) {
  return <li className="sttv-dlc-row" data-dlc-id={id}>
    <SttvResourceImage id={image} className="sttv-dlc-image" />
    <SttvText text={name} />
    <SttvSwitch label={name} checked={checked} disabled={disabled} onChange={onChange} />
  </li>;
}

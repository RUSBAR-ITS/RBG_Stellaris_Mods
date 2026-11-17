import { sttvIcons, type SttvIconName } from '../../assets/icons';
import './controls.css';

export function SttvIcon({ name }: { name: SttvIconName }) {
  return <svg className="sttv-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
    <path d={sttvIcons[name]} />
  </svg>;
}

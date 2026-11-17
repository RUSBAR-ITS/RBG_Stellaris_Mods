import { SttvText } from '../base/Text';
import type { SttvTextRef } from '../../localization/model';
import './status-panel.css';

export function SttvStatusPanel({ message }: { message: SttvTextRef }) {
  return <footer className="sttv-status-panel" role="status" aria-live="polite" aria-atomic="true">
    <SttvText text={message} role="status" />
  </footer>;
}

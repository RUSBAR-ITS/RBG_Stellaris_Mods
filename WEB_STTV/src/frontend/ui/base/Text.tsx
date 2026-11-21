import type { CSSProperties } from 'react';
import { sttvUseLocalization } from '../../localization/context';
import type { SttvTextRef } from '../../localization/model';
import { SttvGameText } from './GameText';

export function SttvText({ text, role = 'body', className = '' }:
  { text: SttvTextRef; role?: string; className?: string }) {
  const { text: resolve } = sttvUseLocalization();
  const style: CSSProperties = { font: `var(--sttv-${role}-font)`, color: `var(--sttv-${role}-color)` };
  return <span className={`sttv-text ${className}`} style={style}><SttvGameText value={resolve(text)} /></span>;
}

import type { ReactNode } from 'react';
import palette from '../../../../config/frontend/game_text_colors.json';
import icons from '../../../../config/frontend/game_text_icons.json';
import { sttvUseLocalization } from '../../localization/context';
import { SttvResourceImage } from './ResourceImage';

function InlineIcon({ name }: { name: keyof typeof icons }) {
  const { text } = sttvUseLocalization();
  return <SttvResourceImage id={'gfx/interface/icons/' + icons[name]} label={text({ id: 'sttv_icon_' + name })}
    className="sttv-inline-icon" />;
}

export function SttvGameText({ value }: { value: string }) {
  if (!value.includes('§') && !value.includes('£')) return value;
  const colors: (keyof typeof palette)[] = [];
  const parts: ReactNode[] = [];
  let start = 0;
  function append(end: number) {
    if (end === start) return;
    const text = value.slice(start, end);
    const code = colors.at(-1);
    parts.push(code ? <span key={start} data-game-color={code} style={{ color: palette[code] }}>{text}</span> : text);
  }
  for (const match of value.matchAll(/§([\w!])|£(\w+)£/gu)) {
    const [, code, icon] = match;
    if (icon) {
      if (!Object.hasOwn(icons, icon)) continue;
      append(match.index);
      parts.push(<InlineIcon key={match.index} name={icon as keyof typeof icons} />);
    } else if (Object.hasOwn(palette, code)) {
      append(match.index);
      colors.push(code as keyof typeof palette);
    } else if (code === '!' && colors.length) {
      append(match.index);
      colors.pop();
    } else continue;
    start = match.index + match[0].length;
  }
  append(value.length);
  return <>{parts}</>;
}

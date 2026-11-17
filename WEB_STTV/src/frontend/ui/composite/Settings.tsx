import { SttvButton } from '../base/Button';
import { SttvSelect } from '../base/Select';
import { SttvText } from '../base/Text';
import type { SttvLanguage } from '../../localization/model';

export function SttvLanguageSelector({ value, onChange }: { value: SttvLanguage; onChange: (value: SttvLanguage) => void }) {
  return <div className="sttv-language-selector">
    <SttvText text={{ id: 'sttv_language' }} role="label" />
    <SttvSelect value={value} onChange={language => onChange(language as SttvLanguage)}
      accessibleName={{ id: 'sttv_language' }} options={[
        { value: 'ru', label: { id: 'sttv_language_ru' } },
        { value: 'en', label: { id: 'sttv_language_en' } },
      ]} />
  </div>;
}
export function SttvThemeToggle({ theme, onToggle }: { theme: string; onToggle: () => void }) {
  const label = { id: theme === 'night' ? 'sttv_day_theme' : 'sttv_night_theme' };
  return <SttvButton icon={theme === 'night' ? 'sun' : 'moon'} accessibleName={label}
    tooltip={{ body: label }} onClick={onToggle} border="hover" />;
}
export function SttvMenuToggle({ expanded, onToggle }: { expanded: boolean; onToggle: () => void }) {
  const label = { id: expanded ? 'sttv_collapse_menu' : 'sttv_expand_menu' };
  return <SttvButton icon={expanded ? 'collapse' : 'expand'} accessibleName={label}
    tooltip={{ body: label }} onClick={onToggle} border="hover" />;
}

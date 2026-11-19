import config from '../../../../config/frontend/zoom.json';
import { SttvSelect } from '../base/Select';
import { SttvText } from '../base/Text';

if (!config.percentages.length || new Set(config.percentages).size !== config.percentages.length
  || config.percentages.some(value => !Number.isFinite(value) || value <= 0)
  || !config.percentages.includes(config.initialPercent)) {
  throw new Error('Invalid field zoom configuration: unique positive percentages must include the initial value.');
}
export const sttvZoomSettings = config;

export function SttvZoomSelector({ value, onChange }: { value: number; onChange: (value: number) => void }) {
  return <div className="sttv-zoom-selector">
    <SttvText text={{ id: 'sttv_zoom' }} role="label" />
    <SttvSelect value={String(value)} onChange={next => onChange(Number(next))}
      accessibleName={{ id: 'sttv_zoom' }} options={config.percentages.map(percent => ({
        value: String(percent), label: { id: 'sttv_zoom_percent', params: { number: percent } },
      }))} />
  </div>;
}

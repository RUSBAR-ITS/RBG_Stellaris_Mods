import type { CSSProperties } from 'react';
import type { SttvCatalog } from '../data/model';
import type { SttvDlcState } from '../app/useDlc';
import { SttvButton } from '../ui/base/Button';
import { SttvText } from '../ui/base/Text';
import { SttvDlcRow } from '../ui/composite/DlcRow';
import { sttvUseLocalization } from '../localization/context';
import config from '../../../config/frontend/dlc.json';
import './dlc-settings.css';

export function SttvDlcSettings({ data, state }: { data: SttvCatalog | null; state: SttvDlcState }) {
  const { language, text } = sttvUseLocalization();
  const names = (data?.definitions.dlcs ?? []).map(entry => ({ id: entry.id!,
    name: { id: entry.texts.find(t => t.sourceRef.pointer === entry.sourceRef.pointer)?.nameId ?? entry.id!, source: 'database' as const } }));
  names.sort((a, b) => text(a.name).localeCompare(text(b.name), language) || a.id.localeCompare(b.id));
  const style = Object.fromEntries(Object.entries(config).filter(([, v]) => typeof v === 'number')
    .map(([key, value]) => [`--sttv-dlc-${key.replace(/[A-Z]/g, v => '-' + v.toLowerCase())}`, `${value}px`])) as CSSProperties;
  Object.assign(style, { '--sttv-switch-width': `${config.switchWidth}px`, '--sttv-switch-height': `${config.switchHeight}px`,
    '--sttv-switch-inset': `${config.switchInset}px` });
  return <section className="sttv-dlc-settings" style={style} aria-label={text({ id: 'sttv_nav_dlc' })}>
    <div className="sttv-dlc-inner">
      <h1><SttvText text={{ id: 'sttv_nav_dlc' }} /></h1>
      {!data ? <p><SttvText text={{ id: 'sttv_no_database' }} /></p> : <>
        {!state.available && <p role="status"><SttvText text={{ id: state.serviceMessage }} /></p>}
        {state.loading && <p role="status"><SttvText text={{ id: 'sttv_dlc_loading' }} /></p>}
        {state.catalogError && <div role="alert"><SttvText text={{ id: 'sttv_dlc_read_failed' }} />
          <SttvButton label={{ id: 'sttv_retry' }} onClick={() => void state.load()} /></div>}
        {state.loaded && !names.length && <p><SttvText text={{ id: 'sttv_dlc_empty' }} /></p>}
        <ul className="sttv-dlc-list">{names.map(row => <SttvDlcRow key={row.id} {...row}
          image={data.presentation?.dlc_icons?.[row.id] ?? null} checked={state.draft.includes(row.id)}
          disabled={state.busy} onChange={() => state.toggle(row.id)} />)}</ul>
        {state.loaded && <div className="sttv-dlc-actions">
          <SttvButton label={{ id: 'sttv_dlc_apply' }} disabled={!state.dirty || state.busy || !state.available} onClick={() => void state.apply()} />
          <SttvButton label={{ id: 'sttv_dlc_discard' }} disabled={!state.dirty || state.busy} onClick={state.discard} />
          {state.busy && <SttvButton label={{ id: 'sttv_cancel' }} onClick={state.cancel} />}
        </div>}
      </>}
    </div>
  </section>;
}

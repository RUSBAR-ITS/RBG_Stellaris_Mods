import type { CSSProperties } from 'react';
import type { useReferenceTree } from '../app/useReferenceTree';
import { SttvButton } from '../ui/base/Button';
import { SttvText } from '../ui/base/Text';
import { SttvDlcRow } from '../ui/composite/DlcRow';
import { sttvUseLocalization } from '../localization/context';
import config from '../../../config/frontend/dlc.json';
import './dlc-settings.css';

export function DlcSettings({ state, referenceMode }: { state: ReturnType<typeof useReferenceTree>; referenceMode: boolean }) {
  const { language } = sttvUseLocalization();
  const style = Object.fromEntries(Object.entries(config)
    .map(([key, value]) => [`--sttv-dlc-${key.replace(/[A-Z]/g, v => '-' + v.toLowerCase())}`, `${value}px`])) as CSSProperties;
  return <div className="sttv-dlc-settings" style={style}><div className="sttv-dlc-inner">
    {state.catalogError ? <div role="alert"><SttvText text={state.catalogError} />
      <SttvButton label={{ id: 'sttv_retry' }} onClick={state.loadDlcs} /></div>
      : !state.dlcs && <p role="status"><SttvText text={{ id: 'sttv_dlc_loading' }} /></p>}
    {state.dlcs && <>
      {!state.dlcs.length && <p><SttvText text={{ id: 'sttv_dlc_empty' }} /></p>}
      <ul className="sttv-dlc-list">{[...state.dlcs].sort((a, b) => a.name[language].localeCompare(b.name[language], language) || a.id.localeCompare(b.id)).map(dlc =>
        <SttvDlcRow key={dlc.id} id={dlc.id} name={{ id: 'sttv_ref_dlc_name', params: { name: dlc.name[language] } }} image={dlc.thumbnail}
          checked={!!state.draft?.includes(dlc.id)} disabled={state.busy} onChange={() => state.toggle(dlc.id)} />)}</ul>
      {state.dirty && <p><SttvText text={{ id: 'sttv_dlc_pending' }} /></p>}
      <div className="sttv-dlc-actions">
        <SttvButton label={{ id: 'sttv_dlc_apply' }} disabled={state.busy || !state.dirty} onClick={() => state.apply(referenceMode)} />
        <SttvButton label={{ id: 'sttv_dlc_discard' }} disabled={state.busy || !state.dirty} onClick={state.discard} />
      </div>
    </>}
  </div></div>;
}

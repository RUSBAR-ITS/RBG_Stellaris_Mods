import { useEffect, useRef, useState } from 'react';
import type { SttvOpening, SttvOpeningController } from '../workers/controller';
import type { SttvTextRef } from '../localization/model';

export function sttvUseDlc(opening: SttvOpening, controller: SttvOpeningController, view: string) {
  const [draft, setDraft] = useState<string[]>([]);
  const [busy, setBusy] = useState(false), [error, setError] = useState<string | null>(null);
  const [catalogError, setCatalogError] = useState(false);
  const operation = useRef(opening.operationId);
  operation.current = opening.operationId;
  const applied = opening.data?.treeCombination.parameters.dlc?.enabled;
  const dataset = opening.data?.datasets.find(d => d.kind === 'dlcs');
  useEffect(() => { setBusy(false); setError(null); setCatalogError(false); setDraft([]); }, [opening.operationId]);
  const appliedKey = applied?.join('|');
  useEffect(() => { if (applied) setDraft([...applied]); }, [appliedKey, opening.operationId]);
  async function load() {
    const id = opening.operationId;
    setCatalogError(false);
    try { await controller.loadDatasets(['dlcs']); }
    catch { if (operation.current === id) setCatalogError(true); }
  }
  useEffect(() => {
    if (view === 'dlc' && dataset?.state === 'not_loaded' && !busy) void load();
  }, [view, dataset?.state, opening.operationId, busy]);
  const dirty = !!applied && (draft.length !== applied.length || draft.some(id => !applied.includes(id)));
  function toggle(id: string) {
    setError(null); setDraft(previous => previous.includes(id) ? previous.filter(value => value !== id) : [...previous, id].sort());
  }
  async function apply() {
    if (busy || !dirty) return;
    const id = opening.operationId;
    setBusy(true); setError(null);
    try { await controller.applyDlc([...draft]); }
    catch (error) {
      if (operation.current === id) setError((error as { code?: string }).code === 'cancelled' ? 'sttv_dlc_cancelled' : 'sttv_dlc_apply_failed');
    } finally { if (operation.current === id) setBusy(false); }
  }
  const service = opening.data?.dlcService;
  const serviceMessage = service?.code === 'set_mismatch' ? 'sttv_dlc_set_mismatch' : 'sttv_dlc_service_unavailable';
  const status: SttvTextRef | null = error ? { id: error } : busy ? { id: 'sttv_dlc_applying' }
    : dirty ? { id: 'sttv_dlc_pending' } : null;
  return { draft, busy, dirty, error, catalogError, status, serviceMessage, available: service?.available === true,
    loading: dataset?.state === 'loading', loaded: dataset?.state === 'loaded', toggle, apply, load,
    discard: () => { setDraft([...(applied ?? [])]); setError(null); }, cancel: () => controller.cancelDlc() };
}
export type SttvDlcState = ReturnType<typeof sttvUseDlc>;

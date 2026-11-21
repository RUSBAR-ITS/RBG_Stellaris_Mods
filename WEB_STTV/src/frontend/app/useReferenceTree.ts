import { useRef, useState } from 'react';
import type { SttvTextRef } from '../localization/model';
import { fetchReference, referenceEndpoint, request, type ServerDlc } from './reference';

function sameSelection(left: string[], right: string[]) {
  return left.length === right.length && left.every(id => right.includes(id));
}
function errorMessage(error: unknown): SttvTextRef {
  return { id: 'sttv_ref_error', params: { reason: error instanceof Error ? error.message : String(error) } };
}

export function useReferenceTree() {
  const [tree, setTree] = useState<Awaited<ReturnType<typeof fetchReference>> | null>(null);
  const [dlcs, setDlcs] = useState<ServerDlc[] | null>(null);
  const [catalogError, setCatalogError] = useState<SttvTextRef | null>(null);
  const [applied, setApplied] = useState<string[]>();
  const [draft, setDraft] = useState<string[]>();
  const [status, setStatus] = useState<SttvTextRef | null>(null);
  const [busy, setBusy] = useState(false);
  const pending = useRef(false), reading = useRef(false);
  const selected = applied ?? dlcs?.map(i => i.id);
  const dirty = !!draft && !!selected && !sameSelection(draft, selected);

  async function run(action: () => Promise<void>) {
    if (pending.current) return;
    pending.current = true;
    setBusy(true);
    setStatus({ id: 'sttv_ref_working' });
    try { await action(); }
    catch (error) { setStatus(errorMessage(error)); }
    finally { pending.current = false; setBusy(false); }
  }
  async function loadDlcs() {
    if (dlcs || reading.current) return;
    reading.current = true;
    setCatalogError(null);
    try {
      const { items } = await request<{ items: ServerDlc[] }>(referenceEndpoint + '/dlcs');
      setDlcs(items);
      setDraft(previous => previous ?? items.map(item => item.id));
    } catch (error) { setCatalogError(errorMessage(error)); }
    finally { reading.current = false; }
  }
  function fetchTree(selection: string[] | undefined, applying: boolean) {
    return run(async () => {
      const result = await fetchReference(selection);
      setTree(result);
      setApplied(result.enabled);
      setDraft(previous => applying ? result.enabled : previous ?? result.enabled);
      setStatus({ id: 'sttv_ref_ready', params: { number: result.nodes.length } });
    });
  }
  function open() {
    if (tree && (!applied || sameSelection(tree.enabled, applied))) return;
    return fetchTree(applied, false);
  }
  function apply(referenceMode: boolean) {
    if (!draft || !dirty || pending.current) return;
    if (referenceMode) return fetchTree(draft, true);
    setApplied(draft);
    if (tree && !sameSelection(tree.enabled, draft)) setTree(null);
    setStatus({ id: 'sttv_dlc_applied' });
  }
  function clear() {
    return run(async () => {
      const result = await request<{ removed_collections: number }>(referenceEndpoint, 'DELETE');
      setTree(null);
      setStatus({ id: 'sttv_ref_removed', params: { number: result.removed_collections } });
    });
  }
  function toggle(id: string) {
    setDraft(prev => prev?.includes(id) ? prev.filter(v => v !== id) : [...prev ?? [], id]);
  }
  return { tree, dlcs, catalogError, draft, status, dirty, busy, open, apply, clear, loadDlcs, toggle, discard: () => setDraft(selected) };
}

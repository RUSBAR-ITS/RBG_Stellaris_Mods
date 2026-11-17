import diagnostics from '../../../config/frontend/diagnostics.json';
import type { SttvOpening } from '../workers/controller';
import type { SttvTextRef } from '../localization/model';

export function sttvStatusMessage(state: SttvOpening): SttvTextRef {
  if (state.status === 'loading') return { id: `sttv_${state.phase ?? 'reading'}` };
  if (state.status === 'error' && state.error) return { id: diagnostics.messages[state.error.code] };
  if (state.status === 'empty') return { id: 'sttv_empty' };
  if (state.status === 'ready') return { id: 'sttv_ready', params: { count: Object.keys(state.data!.technologies).length } };
  return { id: 'sttv_no_database' };
}

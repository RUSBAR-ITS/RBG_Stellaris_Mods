import diagnostics from '../../../config/frontend/diagnostics.json';
import type { SttvOpening } from '../workers/controller';
import type { SttvTextRef } from '../localization/model';
import type { SttvLanguage } from '../localization/model';
import { sttvDatasets } from '../data/registry';
import ru from '../locales/ru.json';
import en from '../locales/en.json';

export function sttvStatusMessage(state: SttvOpening, language: SttvLanguage = 'ru'): SttvTextRef {
  const kind = state.progress?.kind;
  const dictionary: Record<string, string> = language === 'ru' ? ru : en;
  if (state.status === 'loading') return { id: `sttv_${state.phase ?? 'reading'}`,
    params: { index: (state.progress?.fileIndex ?? 0) + 1, total: state.files.length,
      kind: kind ? dictionary[sttvDatasets[kind].labelId] : '' } };
  if (state.status === 'error' && state.error?.code === 'invalid_database_set'
    && typeof state.error.details.count === 'number') return { id: 'sttv_invalid_database_count',
      params: { count: state.error.details.count, expected: state.error.details.expected as number } };
  if (state.status === 'error' && state.error) return { id: diagnostics.messages[state.error.code] };
  if (state.status === 'empty') return { id: 'sttv_empty' };
  if (state.status === 'ready') return { id: 'sttv_ready', params: { count: Object.keys(state.data!.technologies).length } };
  return { id: 'sttv_no_database' };
}

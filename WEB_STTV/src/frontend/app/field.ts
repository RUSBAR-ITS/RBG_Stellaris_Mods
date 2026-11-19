import type { SttvOpening } from '../workers/controller';
import type { SttvLanguage } from '../localization/model';
import { sttvLayout } from '../data/tree/layout';
import { SttvPreparationError, sttvDiagnostic, sttvExceptionDetails } from '../workers/diagnostics';
import dimensions from '../../../config/frontend/interface.json';

export function sttvPrepareField(opening: SttvOpening, language: SttvLanguage, cardHeight = dimensions.cardHeight) {
  if (!opening.data || !['ready', 'empty'].includes(opening.status)) return { layout: null, opening };
  try {
    const layout = sttvLayout(opening.data, language, undefined, { ...dimensions, cardHeight });
    return { layout, opening: { ...opening, diagnostics: [...opening.diagnostics, ...layout.diagnostics] } };
  } catch (error) {
    const diagnostic = error instanceof SttvPreparationError ? error.diagnostic
      : sttvDiagnostic('tree_layout_failed', 'preparing', sttvExceptionDetails(error));
    return { layout: null, opening: { ...opening, status: 'error' as const, error: diagnostic } };
  }
}

import config from '../../../config/frontend/localization.json';
import type { SttvLanguage, SttvLocalizationIndex, SttvOrigin, SttvStoredLocalization } from './model';
import { SttvPreparationError, sttvDiagnostic, sttvInvalid } from '../workers/diagnostics';
import type { SttvDiagnostic } from '../workers/diagnostics';

export class SttvIndexBuilder {
  readonly index: SttvLocalizationIndex = { ru: Object.create(null), en: Object.create(null) };
  private resolvedOrigins = new Map<string, SttvOrigin[]>();

  add(localization: SttvStoredLocalization | undefined, path: string) {
    if (!localization) throw sttvInvalid(path, 'Technology localization enrichment is missing.');
    let nameId = '', descriptionId = '';
    for (const language of config.languages as SttvLanguage[]) {
      for (const field of ['name', 'description'] as const) {
        const recordRef = `${path}/enrichments/localization/${language}/${field}`;
        const value = localization[language]?.[field];
        if (!value || typeof value.requested_key !== 'string') {
          throw sttvInvalid(recordRef, 'Localization address is missing.');
        }
        const id = value.requested_key;
        const previousId = field === 'name' ? nameId : descriptionId;
        if (previousId && previousId !== id) throw sttvInvalid(recordRef, 'String IDs differ between languages.');
        if (field === 'name') nameId = id; else descriptionId = id;
        const origin: SttvOrigin = { recordRef, key: value.key, raw: value.raw,
          source: value.source, inheritedFrom: value.inherited_from,
          unresolvedReferences: value.unresolved_references };
        const existing = this.index[language][id];
        const address = `${language}:${id}`;
        if (existing && existing.text !== null && value.text !== null && existing.text !== value.text) {
          throw new SttvPreparationError(sttvDiagnostic('localization_conflict', 'preparing', {
            source: 'database', language, id,
            texts: [{ text: existing.text, origins: this.resolvedOrigins.get(address) },
              { text: value.text, origins: [origin] }],
          }));
        }
        if (value.text !== null) {
          this.resolvedOrigins.set(address, [...(this.resolvedOrigins.get(address) ?? []), origin]);
        }
        if (!existing) {
          this.index[language][id] = { status: value.text === null ? 'missing' : 'resolved',
            text: value.text, origins: [origin] };
        } else {
          existing.origins.push(origin);
          if (value.text !== null) { existing.text = value.text; existing.status = 'resolved'; }
        }
      }
    }
    return { nameId, descriptionId };
  }

  warnings(): SttvDiagnostic[] {
    return (config.languages as SttvLanguage[]).flatMap(language =>
      Object.entries(this.index[language]).filter(([, record]) => record.status === 'missing')
        .map(([id, record]) => sttvDiagnostic('missing_localization', 'preparing', {
          source: 'database', language, id, recordRefs: record.origins.map(origin => origin.recordRef),
        })));
  }
}

import config from '../../../config/frontend/localization.json';
import type { SttvLanguage, SttvLocalizationIndex, SttvOrigin, SttvStoredLocalization } from './model';
import { SttvPreparationError, sttvDiagnostic, sttvInvalid } from '../workers/diagnostics';
import type { SttvDiagnostic } from '../workers/diagnostics';
import type { SttvDatabaseKind } from '../data/model';
import { sttvDatabaseKinds } from '../data/registry';

export class SttvIndexBuilder {
  readonly index: SttvLocalizationIndex = { ru: Object.create(null), en: Object.create(null) };
  private resolvedOrigins = new Map<string, SttvOrigin[]>();

  add(localization: SttvStoredLocalization | undefined, path: string,
    database: SttvDatabaseKind = 'technologies', descriptionOnly = false,
    roles: ('name' | 'description')[] = descriptionOnly ? ['description'] : ['name', 'description']) {
    if (!localization) throw sttvInvalid(path, 'Object localization enrichment is missing.');
    let nameId = '', descriptionId = '';
    for (const language of config.languages as SttvLanguage[]) {
      for (const field of roles) {
        const recordRef = `${path}/enrichments/localization/${language}/${field}`;
        const value = localization[language]?.[field];
        if (!value || typeof value.requested_key !== 'string') {
          throw sttvInvalid(recordRef, 'Localization address is missing.');
        }
        const id = value.requested_key;
        const previousId = field === 'name' ? nameId : descriptionId;
        if (previousId && previousId !== id) throw sttvInvalid(recordRef, 'String IDs differ between languages.');
        if (field === 'name') nameId = id; else descriptionId = id;
        const origin: SttvOrigin = { recordRef: { database, pointer: recordRef }, key: value.key, raw: value.raw,
          source: value.source, inheritedFrom: value.inherited_from ? { database, pointer: value.inherited_from } : null,
          ...(value.fallback ? { fallback: { kind: value.fallback.kind,
            sourceRef: { database, pointer: value.fallback.source_ref } } } : {}),
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

  orderOrigins() {
    for (const language of config.languages as SttvLanguage[]) {
      for (const record of Object.values(this.index[language])) record.origins.sort((left, right) =>
        sttvDatabaseKinds.indexOf(left.recordRef.database) - sttvDatabaseKinds.indexOf(right.recordRef.database)
        || left.recordRef.pointer.localeCompare(right.recordRef.pointer, 'en', { numeric: true }));
    }
  }

  warnings(): SttvDiagnostic[] {
    return (config.languages as SttvLanguage[]).flatMap(language =>
      Object.entries(this.index[language]).sort(([a], [b]) => a.localeCompare(b, 'en')).filter(([, record]) => record.status === 'missing')
        .map(([id, record]) => sttvDiagnostic('missing_localization', 'preparing', {
          source: 'database', language, id, recordRefs: record.origins.map(origin => origin.recordRef),
        })));
  }
}

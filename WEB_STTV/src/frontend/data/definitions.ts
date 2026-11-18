import { sttvDatasets } from './registry';
import type { SttvDatabaseKind, SttvDefinition, SttvNodeRef } from './model';
import { sttvDocument, sttvField, sttvItems, sttvScalar, type SttvDatabase } from './syntax';
import { sttvDefinitionTexts, type SttvTargetRules } from './textTargets';
import type { SttvIndexBuilder } from '../localization/index';
import { sttvInvalid } from '../workers/diagnostics';

export function sttvAdaptDefinitions(db: SttvDatabase, kind: SttvDatabaseKind,
  rules: SttvTargetRules, strings: SttvIndexBuilder,
  partial?: { definitions: SttvDefinition[]; index: Record<string, SttvNodeRef[]>; documentOffset: number }) {
  const spec = sttvDatasets[kind], definitions: SttvDefinition[] = partial?.definitions ?? [];
  const index: Record<string, SttvNodeRef[]> = partial?.index ?? Object.create(null);
  db.documents.forEach((document, d) => {
    d += partial?.documentOffset ?? 0;
    const file = sttvDocument(document, `/documents/${d}`);
    if (!file.startsWith(spec.directory + '/') || !file.endsWith('.txt')) return;
    if (!spec.recursive && file.slice(0, file.lastIndexOf('/')) !== spec.directory) return;
    document.items.forEach((node, i) => {
      if (node.kind !== 'assignment' || node.operator !== '=' || node.value?.kind !== 'block') return;
      const pointer = `/documents/${d}/items/${i}`, type = sttvScalar(node.key, pointer);
      if (spec.rootTypes.length && !(spec.rootTypes as string[]).includes(type)) return;
      const items = sttvItems(node.value, pointer), sourceRef = { database: kind, pointer };
      const id = spec.identity === 'anonymous' ? undefined : spec.idField
        ? sttvScalar(sttvField(items, spec.idField, pointer), pointer) : type;
      if (id !== undefined) {
        if (!id) throw sttvInvalid(sourceRef, 'Empty object ID.');
        if (index[id] && spec.identity !== 'fragments') {
          const error = sttvInvalid(sourceRef, `Duplicate ${kind} ID: ${id}`);
          error.diagnostic.details.previousSourceRef = index[id][0];
          throw error;
        }
        (index[id] ??= []).push(sourceRef);
      }
      definitions.push({ sourceRef, type, ...(id === undefined ? {} : { id }),
        ...sttvDefinitionTexts(node, pointer, id ?? type, kind, rules, strings) });
    });
  });
  return { definitions, index };
}

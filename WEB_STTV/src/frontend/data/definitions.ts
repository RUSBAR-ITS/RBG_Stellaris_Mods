import { sttvDatasets } from './registry';
import type { SttvDatabaseKind, SttvDefinition, SttvNodeRef } from './model';
import { sttvDocument, sttvField, sttvItems, sttvScalar, type SttvDatabase } from './syntax';
import { sttvDefinitionTexts, type SttvTargetRules } from './textTargets';
import type { SttvIndexBuilder } from '../localization/index';
import { sttvInvalid } from '../workers/diagnostics';
import { sttvSelectedNodes } from './objectSelection';

export function sttvAdaptDefinitions(db: SttvDatabase, kind: SttvDatabaseKind,
  rules: SttvTargetRules, strings: SttvIndexBuilder,
  partial?: { definitions: SttvDefinition[]; index: Record<string, SttvNodeRef[]>; itemOffset: number }) {
  const spec = sttvDatasets[kind], definitions: SttvDefinition[] = partial?.definitions ?? [];
  const index: Record<string, SttvNodeRef[]> = partial?.index ?? Object.create(null);
  [db].forEach(document => {
    strings.documentId = db.document_id;
    const file = sttvDocument(document, '');
    if (!spec.sourceRoles && (!file.startsWith(spec.directory + '/') || !file.endsWith('.txt'))) return;
    if (!spec.recursive && file.slice(0, file.lastIndexOf('/')) !== spec.directory) return;
    sttvSelectedNodes(kind, document.items, file, partial?.itemOffset ?? 0).forEach(({ node, pointer }) => {
      const type = sttvScalar(node.key, pointer);
      const items = sttvItems(node.value, pointer), sourceRef = { database: kind, document_id: db.document_id, pointer };
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
      const texts = sttvDefinitionTexts(node, pointer, id ?? type, kind, rules, strings);
      const descriptorRefs = node.enrichments?.dlc?.descriptors;
      if (spec.descriptorLink) {
        const name = sttvScalar(sttvField(items, spec.descriptorLink.matchField, pointer), pointer);
        const nameId = texts.texts.find(text => text.sourceRef.pointer === pointer)?.nameId;
        if (nameId) for (const language of ['ru', 'en'] as const) {
          const record = strings.index[language][nameId];
          if (record?.status === 'missing') record.fallbackText = name;
        }
      }
      definitions.push({ sourceRef, type, ...(id === undefined ? {} : { id }), ...texts,
        ...(descriptorRefs ? { descriptorRefs } : {}) });
    });
  });
  return { definitions, index };
}

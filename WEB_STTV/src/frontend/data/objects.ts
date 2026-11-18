import config from '../../../config/frontend/adapter.json';
import type { SttvObjectCatalog } from './model';
import type { SttvDatabase, SttvNode } from './syntax';
import { sttvField, sttvFields, sttvItems, sttvScalar, sttvDocument } from './syntax';
import { sttvReadRequirements } from './requirements';
import type { SttvIndexBuilder } from '../localization/index';
import { sttvInvalid } from '../workers/diagnostics';

export function sttvAdaptObjects(db: SttvDatabase, kind: 'components' | 'buildings',
  strings: SttvIndexBuilder, partial?: { catalog: SttvObjectCatalog; documentOffset: number }): SttvObjectCatalog {
  const { objects, requirements, upgrades }: SttvObjectCatalog = partial?.catalog ?? {
    objects: Object.create(null), requirements: [], upgrades: [] };
  const selection = config.objects[kind], fields = config.fields;
  const ref = (pointer: string) => ({ database: kind, pointer });
  db.documents.forEach((document, d) => {
    d += partial?.documentOffset ?? 0;
    const file = sttvDocument(document, `/documents/${d}`);
    if (!file.startsWith(`${selection.directory}/`) || !file.endsWith('.txt')) return;
    document.items.forEach((node, i) => {
      if (node.kind !== 'assignment' || node.value?.kind !== 'block') return;
      const pointer = `/documents/${d}/items/${i}`;
      const root = sttvScalar(node.key, pointer);
      if (selection.rootTypes.length && !(selection.rootTypes as string[]).includes(root)) return;
      const items = sttvItems(node.value, pointer);
      const id = selection.idField ? sttvScalar(sttvField(items, selection.idField, pointer), pointer) : root;
      if (!id) throw sttvInvalid(pointer, 'Object ID must not be empty.');
      if (objects[id]) {
        const error = sttvInvalid(pointer, `Duplicate ${kind} ID: ${id}`);
        error.diagnostic.details.previousSourceRef = objects[id].sourceRef;
        throw error;
      }
      const prerequisite = sttvFields(items, fields.prerequisites)[0];
      const prerequisitePath = prerequisite ? `${pointer}/value/items/${prerequisite.index}/value` : pointer;
      const parsed = sttvReadRequirements(sttvField(items, fields.prerequisites, pointer), prerequisitePath, id, true);
      objects[id] = { id, sourceRef: ref(pointer), prerequisites: parsed.prerequisites,
        ...(kind === 'components' ? { templateType: root } : {}),
        prerequisitesRef: prerequisite ? ref(prerequisitePath) : null,
        ...strings.add(node.enrichments?.localization, pointer, kind), conditionalDescriptions: [] };
      requirements.push(...parsed.links.map(link => ({ from: { database: 'technologies' as const, id: link.from },
        to: { database: kind, id }, requirementPaths: link.requirementPaths, sourceRef: ref(prerequisitePath) })));
      if (kind === 'buildings') {
        for (const { node: description, index } of sttvFields(items, fields.description)) {
          if (description.value?.kind !== 'block') continue;
          const path = `${pointer}/value/items/${index}`;
          const trigger = sttvFields(sttvItems(description.value, path), fields.trigger);
          if (trigger.length > 1) throw sttvInvalid(path, 'Ambiguous description trigger.');
          objects[id].conditionalDescriptions.push({ sourceRef: ref(path),
            descriptionId: strings.add(description.enrichments?.localization, path, kind, true).descriptionId,
            triggerRef: trigger.length ? ref(`${path}/value/items/${trigger[0].index}/value`) : null });
        }
      }
      const upgrade = sttvFields(items, selection.upgradeField);
      if (upgrade.length > 1) throw sttvInvalid(pointer, 'Ambiguous upgrade field.');
      if (upgrade.length) {
        const path = `${pointer}/value/items/${upgrade[0].index}/value`;
        const value = upgrade[0].node.value;
        const values: SttvNode[] = kind === 'components' ? [value!] : sttvItems(value, path);
        values.forEach((target, n) => upgrades.push({ from: { database: kind, id },
          to: { database: kind, id: sttvScalar(target, path) },
          sourceRef: ref(kind === 'components' ? path : `${path}/items/${n}`) }));
      }
    });
  });
  return { objects, requirements, upgrades };
}

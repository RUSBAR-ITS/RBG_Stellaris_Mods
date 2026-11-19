import type { SttvDatabaseKind, SttvDefinitionText } from './model';
import type { SttvNode } from './syntax';
import { sttvFields, sttvScalar } from './syntax';
import { sttvInvalid } from '../workers/diagnostics';
import type { SttvIndexBuilder } from '../localization/index';

type SttvTextRole = 'name' | 'description';
export interface SttvTargetRules {
  keys: {
    name_prefix?: string; name_field?: string; omit_name?: boolean;
    description_suffix: string | null; description_field: string | null;
    description_nodes?: boolean; description_excluded?: string[]; text_field: string;
    child_text_fields?: { field: string; role: string }[];
    endpoint_fields?: string[]; endpoint_description_suffix?: string;
  };
}
export type SttvTargetRegistry = Partial<Record<SttvDatabaseKind, SttvTargetRules>>;

export function sttvDefinitionTexts(root: SttvNode, pointer: string, id: string,
  database: SttvDatabaseKind, rules: SttvTargetRules, strings: SttvIndexBuilder) {
  const keys = rules.keys, texts: SttvDefinitionText[] = [];
  const items = root.value!.items!;
  function add(node: SttvNode, path: string, expected: Partial<Record<SttvTextRole, string>>) {
    const roles = Object.keys(expected) as SttvTextRole[];
    if (!roles.length) return;
    for (const language of ['ru', 'en'] as const) {
      for (const role of roles) {
        if (node.enrichments?.localization?.[language]?.[role]?.requested_key !== expected[role]) {
          throw sttvInvalid({ database, document_id: strings.documentId, pointer: path }, `Missing or mismatched ${role} enrichment.`);
        }
      }
    }
    const localized = strings.add(node.enrichments?.localization, path, database, false, roles);
    texts.push({ sourceRef: { database, document_id: strings.documentId, pointer: path },
      ...(roles.includes('name') ? { nameId: localized.nameId } : {}),
      ...(roles.includes('description') ? { descriptionId: localized.descriptionId } : {}) });
  }
  function descendants(node: SttvNode, path: string) {
    if (node.value?.kind === 'scalar') {
      add(node, path, { description: sttvScalar(node.value, path) });
      return;
    }
    if (node.value?.kind !== 'block') throw sttvInvalid(path, 'Unsupported description form.');
    const excluded = keys.description_excluded ?? ['trigger', 'limit', 'exclusive_trigger'];
    for (const [i, child] of (node.value.items ?? []).entries()) {
      if (child.kind !== 'assignment' || child.operator !== '=') continue;
      const childPath = `${path}/value/items/${i}`;
      if (child.key?.text === keys.text_field) add(child, childPath, { description: sttvScalar(child.value, childPath) });
      else if (!excluded.includes(child.key?.text ?? '') && child.value?.kind === 'block') descendants(child, childPath);
    }
  }
  const expected: Partial<Record<SttvTextRole, string>> = {};
  const base = (keys.name_prefix ?? '') + id;
  if (keys.name_field) {
    const fields = sttvFields(items, keys.name_field);
    if (fields.length > 1) throw sttvInvalid(pointer, 'Ambiguous name field.');
    if (fields.length) expected.name = sttvScalar(fields[0].node.value, pointer);
  } else if (!keys.omit_name) expected.name = base;
  if (keys.description_suffix !== null) expected.description = base + keys.description_suffix;
  const descriptions = keys.description_field ? sttvFields(items, keys.description_field) : [];
  const direct = !keys.description_nodes && descriptions.length === 1 && descriptions[0].node.value?.kind === 'scalar';
  if (direct) expected.description = sttvScalar(descriptions[0].node.value, pointer);
  add(root, pointer, expected);
  if (!direct) for (const { node, index } of descriptions) {
    const path = `${pointer}/value/items/${index}`;
    const values = sttvFields(node.value?.items ?? [], keys.text_field);
    if (!keys.description_nodes && values.length === 1) add(node, path, { description: sttvScalar(values[0].node.value, path) });
    else descendants(node, path);
  }
  for (const field of keys.child_text_fields ?? []) {
    for (const { node, index } of sttvFields(items, field.field)) {
      const path = `${pointer}/value/items/${index}`;
      add(node, path, { [field.role]: sttvScalar(node.value, path) });
    }
  }
  const endpoints: Record<string, { id: string; sourceRef: { database: SttvDatabaseKind; document_id: string; pointer: string } }> = {};
  for (const field of keys.endpoint_fields ?? []) {
    const values = sttvFields(items, field);
    if (values.length !== 1) throw sttvInvalid(pointer, `Missing or ambiguous endpoint: ${field}`);
    const { node, index } = values[0], path = `${pointer}/value/items/${index}`;
    const key = sttvScalar(node.value, path);
    add(node, path, { name: key, description: key + keys.endpoint_description_suffix });
    endpoints[field] = { id: key, sourceRef: { database, document_id: strings.documentId, pointer: path } };
  }
  return { texts, ...(Object.keys(endpoints).length ? { endpoints } : {}) };
}

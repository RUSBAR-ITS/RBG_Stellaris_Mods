import { sttvDatasets, type SttvDatabaseKind } from './registry';
import type { SttvNode } from './syntax';
import { sttvSetError } from './setMetadata';

export function sttvSourceRole(kind: SttvDatabaseKind, file: string) {
  const roles = sttvDatasets[kind].sourceRoles;
  if (!roles) return 'objects';
  const matches = roles.filter(row => new RegExp('^' + row.pattern.split('*')
    .map(part => part.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('.*') + '$').test(file));
  if (matches.length !== 1) sttvSetError('Source role is not configured.', { kind, file });
  return matches[0].role;
}

export function sttvSelectedNodes(kind: SttvDatabaseKind, items: SttvNode[], file: string, offset = 0) {
  const selected: { pointer: string; node: SttvNode }[] = [];
  if (sttvSourceRole(kind, file) === 'descriptor') return selected;
  const spec = sttvDatasets[kind], containers = spec.containers ?? [];
  function walk(nodes: SttvNode[], prefix: string, depth: number) {
    nodes.forEach((node, i) => {
      if (node?.kind !== 'assignment' || node.value?.kind !== 'block') return;
      const pointer = `${prefix}/${i + (depth === 0 ? offset : 0)}`;
      if (depth < containers.length) {
        if (node.key?.text === containers[depth]) walk(node.value.items ?? [], pointer + '/value/items', depth + 1);
      } else if (!spec.rootTypes.length || spec.rootTypes.includes(node.key?.text ?? '')) selected.push({ pointer, node });
    });
  }
  walk(items, '/items', 0);
  return selected;
}

export function sttvObjectPointer(kind: SttvDatabaseKind, pointer: string, file: string) {
  if (sttvSourceRole(kind, file) === 'descriptor') return false;
  return new RegExp('^/items/(0|[1-9]\\d*)' + '(?:/value/items/(0|[1-9]\\d*))'
    .repeat(sttvDatasets[kind].containers?.length ?? 0) + '$').test(pointer);
}

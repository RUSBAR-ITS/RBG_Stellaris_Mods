import type { SttvNodeRef } from '../model';
import type { SttvTreeRecord } from './model';
import { sttvRecord, sttvTreeError } from './contract';

export function sttvTreeRecord(value: unknown, combinationId: string, sourceRef: SttvNodeRef): SttvTreeRecord {
  const row = sttvRecord(value) && Object.hasOwn(value, combinationId) ? value[combinationId] : undefined;
  if (!sttvRecord(row) || !['root', 'resolved', 'ambiguous'].includes(String(row.status))
    || !(row.parent_tech === null || typeof row.parent_tech === 'string' && row.parent_tech.length > 0)
    || !Array.isArray(row.children) || !row.children.every(child => typeof child === 'string' && child.length > 0)
    || new Set(row.children).size !== row.children.length
    || (row.status === 'resolved') !== (row.parent_tech !== null)) {
    sttvTreeError('tree_enrichment_invalid', 'Missing or invalid tree record.', { combinationId, sourceRef });
  }
  return { parent_tech: row.parent_tech as string | null, children: [...row.children], status: row.status as SttvTreeRecord['status'] };
}

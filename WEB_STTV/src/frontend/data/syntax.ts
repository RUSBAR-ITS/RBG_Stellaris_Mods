import { sttvInvalid } from '../workers/diagnostics';
import type { SttvStoredLocalization } from '../localization/model';

// Only the fields consumed by the adapter are described here.
export interface SttvNode {
  kind: string;
  text?: string;
  key?: SttvNode;
  operator?: string;
  value?: SttvNode;
  body?: SttvNode;
  items?: SttvNode[];
  enrichments?: { localization?: SttvStoredLocalization };
}
export interface SttvDatabase {
  format: string;
  format_version: number;
  documents: { source: { file: string; root: string }; items: SttvNode[] }[];
}
export function sttvItems(node: SttvNode | undefined, path: string): SttvNode[] {
  if (node?.kind !== 'block' || !Array.isArray(node.items)) {
    throw sttvInvalid(path, 'A block is required for this transformation.');
  }
  return node.items;
}
export function sttvScalar(node: SttvNode | undefined, path: string): string {
  if (node?.kind !== 'scalar' || typeof node.text !== 'string') {
    throw sttvInvalid(path, 'A scalar is required for this transformation.');
  }
  return node.text;
}
export function sttvFields(items: SttvNode[], name: string) {
  return items.flatMap((node, index) =>
    node.kind === 'assignment' && node.key?.text === name ? [{ node, index }] : []);
}
export function sttvField(items: SttvNode[], name: string, path: string) {
  const matches = sttvFields(items, name);
  if (matches.length > 1) throw sttvInvalid(path, `Ambiguous field: ${name}`);
  return matches[0]?.node.value;
}

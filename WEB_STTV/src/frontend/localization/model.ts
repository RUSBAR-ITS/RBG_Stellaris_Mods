export type SttvLanguage = 'ru' | 'en';
export interface SttvOrigin {
  recordRef: SttvNodeRef;
  key: string | null;
  raw: string | null;
  source: { tier: string; file: string; line: number } | null;
  inheritedFrom: SttvNodeRef | null;
  fallback?: { kind: 'component_set'; sourceRef: SttvNodeRef } | { kind: 'dlc_descriptor'; sourceRef: SttvDocumentRef };
  unresolvedReferences: string[];
}
export interface SttvLocalizedRecord {
  status: 'resolved' | 'missing';
  text: string | null;
  origins: SttvOrigin[];
  fallbackText?: string;
}
export type SttvLocalizationIndex = Record<SttvLanguage, Record<string, SttvLocalizedRecord>>;
export interface SttvStoredString {
  requested_key: string;
  key: string | null;
  raw: string | null;
  text: string | null;
  source: SttvOrigin['source'];
  inherited_from: SttvNodeRef | null;
  unresolved_references: string[];
  fallback?: { kind: 'component_set'; source_ref: SttvNodeRef } | { kind: 'dlc_descriptor'; source_ref: SttvDocumentRef };
  candidate_keys?: string[];
}
export type SttvStoredLocalization = Record<SttvLanguage,
  { name?: SttvStoredString; description?: SttvStoredString }>;
export interface SttvTextRef {
  id: string;
  source?: 'builtin' | 'database';
  params?: Record<string, string | number>;
  suffix?: SttvTextRef;
}
import type { SttvNodeRef } from '../data/model';
export type SttvDocumentRef = Omit<SttvNodeRef, 'pointer'>;

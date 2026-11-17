export type SttvLanguage = 'ru' | 'en';
export interface SttvOrigin {
  recordRef: string;
  key: string | null;
  raw: string | null;
  source: { tier: string; file: string; line: number } | null;
  inheritedFrom: string | null;
  unresolvedReferences: string[];
}
export interface SttvLocalizedRecord {
  status: 'resolved' | 'missing';
  text: string | null;
  origins: SttvOrigin[];
}
export type SttvLocalizationIndex = Record<SttvLanguage, Record<string, SttvLocalizedRecord>>;
export interface SttvStoredString {
  requested_key: string;
  key: string | null;
  raw: string | null;
  text: string | null;
  source: SttvOrigin['source'];
  inherited_from: string | null;
  unresolved_references: string[];
}
export type SttvStoredLocalization = Record<SttvLanguage,
  { name: SttvStoredString; description: SttvStoredString }>;
export interface SttvTextRef {
  id: string;
  source?: 'builtin' | 'database';
  params?: Record<string, string | number>;
  suffix?: SttvTextRef;
}

export type SttvLanguage = 'ru' | 'en';
export interface SttvLocalizedRecord { status: 'resolved' | 'missing'; text: string | null }
export type SttvLocalizationIndex = Record<SttvLanguage, Record<string, SttvLocalizedRecord>>;
export interface SttvTextRef {
  id: string; source?: 'builtin' | 'database'; params?: Record<string, string | number>; suffix?: SttvTextRef;
}

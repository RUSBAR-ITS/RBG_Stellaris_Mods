import config from '../../../config/frontend/localization.json';
import ru from '../locales/ru.json';
import en from '../locales/en.json';
import { sttvLookup, sttvSource } from './lookup';
import type { SttvLanguage, SttvTextRef } from './model';

const sttvBuiltin = sttvSource(config.sources.builtin.reader, { ru, en }, config.sources.builtin.path);
export function sttvCreateTextLookup(data: unknown, language: SttvLanguage) {
  const sources = { builtin: sttvBuiltin,
    database: sttvSource(config.sources.database.reader, data, config.sources.database.path) };
  return (ref: SttvTextRef) => sttvLookup(sources, language, ref);
}

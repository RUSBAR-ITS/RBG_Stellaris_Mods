import { expect, type Page } from '@playwright/test';
import { sttvBrowserDatabase, sttvSet } from '../fixtures';
import type { SttvDatabase } from '../../../src/frontend/data/syntax';
import ru from '../../../src/frontend/locales/ru.json' with { type: 'json' };
import en from '../../../src/frontend/locales/en.json' with { type: 'json' };
import { mkdirSync, mkdtempSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { sttvBundle } from '../manifestFixtures';

export { ru, en };
export async function sttvEnglish(page: Page) {
  await page.getByRole('button', { name: ru.sttv_language, exact: true }).click();
  await page.getByRole('option', { name: 'English', exact: true }).click();
  await expect(page.locator('html')).toHaveAttribute('lang', 'en');
}
export async function sttvUpload(page: Page, data: unknown = sttvBrowserDatabase()) {
  await sttvUploadEntries(page, sttvBundle(sttvSet(data as SttvDatabase)).entries);
}
export async function sttvUploadEntries(page: Page, entries: { path: string; content: string }[]) {
  const base = resolve('data/frontend-tests/directories'); mkdirSync(base, { recursive: true });
  const directory = mkdtempSync(resolve(base, 'set-'));
  for (const entry of entries) {
    const path = resolve(directory, entry.path);
    if (!path.startsWith(directory + '/'.replace('/', process.platform === 'win32' ? '\\' : '/'))) throw new Error('Unsafe test path');
    mkdirSync(dirname(path), { recursive: true }); writeFileSync(path, entry.content);
  }
  await page.locator('input[type=file]').setInputFiles(directory);
}
export async function sttvReady(page: Page) {
  await sttvUpload(page);
  await expect(page.locator('[data-technology-id]')).toHaveCount(18);
}
export async function sttvOffset(page: Page) {
  return page.locator('#sttv-viewport-content').evaluate(element => ({ x: element.scrollLeft, y: element.scrollTop }));
}

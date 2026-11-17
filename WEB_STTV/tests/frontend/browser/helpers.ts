import { expect, type Page } from '@playwright/test';
import { sttvBrowserDatabase } from '../fixtures';
import ru from '../../../src/frontend/locales/ru.json' with { type: 'json' };
import en from '../../../src/frontend/locales/en.json' with { type: 'json' };

export { ru, en };
export async function sttvEnglish(page: Page) {
  await page.getByRole('button', { name: ru.sttv_language, exact: true }).click();
  await page.getByRole('option', { name: 'English', exact: true }).click();
  await expect(page.locator('html')).toHaveAttribute('lang', 'en');
}
export async function sttvUpload(page: Page, data: unknown = sttvBrowserDatabase()) {
  await page.locator('input[type=file]').setInputFiles({ name: 'fixture.json', mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify(data)) });
}
export async function sttvReady(page: Page) {
  await sttvUpload(page);
  await expect(page.locator('[data-technology-id]')).toHaveCount(18);
}
export async function sttvOffset(page: Page) {
  return page.locator('#sttv-viewport-content').evaluate(element => ({ x: element.scrollLeft, y: element.scrollTop }));
}

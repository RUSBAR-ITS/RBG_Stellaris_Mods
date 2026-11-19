import { test, expect } from '@playwright/test';
import { sttvEnglish, sttvReady, sttvUploadEntries, en } from './helpers';
import { sttvSet, sttvBrowserDatabase } from '../fixtures';
import { sttvBundle } from '../manifestFixtures';

test('directory files may be reordered; missing declarations clear every card', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  const bundle = sttvBundle(sttvSet(sttvBrowserDatabase()));
  await sttvUploadEntries(page, bundle.entries.reverse());
  await expect(page.locator('[data-technology-id]')).toHaveCount(18);
  await sttvUploadEntries(page, bundle.entries.filter(row => !row.path.includes('/events/')));
  await expect(page.getByRole('status')).toHaveText(en.sttv_diagnostic_invalid_database_set);
  await expect(page.locator('[data-technology-id]')).toHaveCount(0);
});
test('unsupported manifest and corrupt technology fail; retry repeats the directory snapshot', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page); await sttvReady(page);
  await sttvUploadEntries(page, [{ path: 'manifest.json', content: '{"format":"sttv.parse_database","format_version":6}' }]);
  await expect(page.getByRole('status')).toHaveText(en.sttv_diagnostic_invalid_database_set);
  await page.getByRole('button', { name: en.sttv_retry, exact: true }).click();
  await expect(page.getByRole('status')).toHaveText(en.sttv_diagnostic_invalid_database_set);
  const bundle = sttvBundle(sttvSet(sttvBrowserDatabase()));
  const file = bundle.entries.find(row => row.path.includes('/technologies/'))!;
  file.content += ' ';
  await sttvUploadEntries(page, bundle.entries);
  await expect(page.getByRole('status')).toHaveText(en.sttv_diagnostic_invalid_database_set);
  await expect(page.locator('[data-technology-id]')).toHaveCount(0);
});

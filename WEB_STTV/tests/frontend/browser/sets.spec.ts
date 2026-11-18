import { test, expect } from '@playwright/test';
import { sttvEnglish, sttvReady, en } from './helpers';
import { sttvSet, sttvBrowserDatabase } from '../fixtures';
import type { SttvDatabase } from '../../../src/frontend/data/syntax';

function sttvFiles(inputs: SttvDatabase[]) {
  return inputs.map((db, i) => ({ name: `renamed-${i}.json`, mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify(db)) }));
}
test('set roles survive reordered files and invalid replacement clears every card', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  await page.locator('input[type=file]').setInputFiles(sttvFiles(sttvSet(sttvBrowserDatabase()).reverse()));
  await expect(page.locator('[data-technology-id]')).toHaveCount(18);
  for (const count of [1, 14, 16]) {
    const files = sttvSet();
    while (files.length < count) files.push(files[0]);
    await page.locator('input[type=file]').setInputFiles(sttvFiles(files.slice(0, count)));
    await expect(page.getByRole('status')).toHaveText(en.sttv_invalid_database_count.replace('{expected}', '15').replace('{count}', String(count)));
    await expect(page.locator('[data-technology-id]')).toHaveCount(0);
  }
});
test('mixed identity and duplicate roles fail; explicit retry repeats the whole selection', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page); await sttvReady(page);
  const inputs = sttvSet(); inputs[2].dataset!.set_id = 'b'.repeat(64);
  await page.locator('input[type=file]').setInputFiles(sttvFiles(inputs));
  await expect(page.getByRole('status')).toHaveText(en.sttv_diagnostic_invalid_database_set);
  await page.getByRole('button', { name: en.sttv_retry, exact: true }).click();
  await expect(page.getByRole('status')).toHaveText(en.sttv_diagnostic_invalid_database_set);
  const duplicates = sttvSet(); duplicates[14] = duplicates[0];
  await page.locator('input[type=file]').setInputFiles(sttvFiles(duplicates));
  await expect(page.getByRole('status')).toHaveText(en.sttv_diagnostic_invalid_database_set);
  await expect(page.locator('[data-technology-id]')).toHaveCount(0);
});

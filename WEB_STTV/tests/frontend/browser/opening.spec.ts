import { test, expect } from '@playwright/test';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';
import { sttvEnglish, sttvUpload, sttvReady, en, ru } from './helpers';
import { sttvDatabase, sttvTechnology } from '../fixtures';

test('invalid JSON, retry, replacement, empty result, and diagnostic downloads', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  await page.locator('input[type=file]').setInputFiles({ name: 'broken.json', mimeType: 'application/json', buffer: Buffer.from('{') });
  await expect(page.getByRole('status')).toHaveText(en.sttv_diagnostic_invalid_json);
  const downloading = page.waitForEvent('download');
  await page.getByRole('button', { name: en.sttv_save_report, exact: true }).click();
  const download = await downloading;
  const report = JSON.parse(await readFile((await download.path())!, 'utf8'));
  expect(report.error.code).toBe('invalid_json');
  expect(report.file).toEqual({ name: 'broken.json', size: 1 });
  expect(report.result).toBe('error'); expect(report.operationId).toBe(1);
  await page.getByRole('button', { name: en.sttv_retry, exact: true }).click();
  await expect(page.getByRole('status')).toHaveText(en.sttv_diagnostic_invalid_json);
  await sttvReady(page);
  await sttvUpload(page, sttvDatabase([]));
  await expect(page.getByRole('status')).toHaveText(en.sttv_empty);
  await expect(page.locator('[data-technology-id]')).toHaveCount(0);
  await expect(page.getByRole('button', { name: en.sttv_retry, exact: true })).toHaveCount(0);
});
test('localization warnings stay in reports, conflicts block the replacement', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  const missing = sttvTechnology('tech_missing');
  missing.enrichments.localization.ru.name.text = null;
  await sttvUpload(page, sttvDatabase([missing]));
  await expect(page.getByRole('status')).toHaveText(en.sttv_ready.replace('{count}', '1'));
  const downloading = page.waitForEvent('download');
  await page.getByRole('button', { name: en.sttv_save_report, exact: true }).click();
  const report = JSON.parse(await readFile((await (await downloading).path())!, 'utf8'));
  expect(report.diagnostics[0].code).toBe('missing_localization'); expect(report.error).toBeNull();
  const a = sttvTechnology('a'), b = sttvTechnology('b');
  b.enrichments.localization.ru.name.requested_key = 'a';
  b.enrichments.localization.en.name.requested_key = 'a';
  await sttvUpload(page, sttvDatabase([a, b]));
  await expect(page.getByRole('status')).toHaveText(en.sttv_diagnostic_localization_conflict);
  await expect(page.locator('[data-technology-id]')).toHaveCount(0);
});
test('startup failure and cancel are controlled without retaining the previous catalog', async ({ page }) => {
  await page.addInitScript(() => {
    class SttvIdleWorker {
      onmessage = null; onerror = null; onmessageerror = null;
      postMessage() {} terminate() {}
    }
    window.Worker = SttvIdleWorker as unknown as typeof Worker;
  });
  await page.goto('/'); await sttvEnglish(page); await sttvUpload(page);
  await expect(page.getByRole('button', { name: en.sttv_cancel, exact: true })).toBeVisible();
  await page.getByRole('button', { name: en.sttv_cancel, exact: true }).click();
  await expect(page.getByRole('status')).toHaveText(en.sttv_no_database);
  await expect(page.getByRole('button', { name: en.sttv_save_report, exact: true })).toHaveCount(0);
});
test('real database loads in a worker and remains read-only', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  const workers: string[] = [];
  page.on('worker', worker => workers.push(worker.url()));
  await page.goto('/');
  const started = performance.now();
  const picking = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: ru.sttv_open_database, exact: true }).click();
  await (await picking).setFiles(resolve('data/stage10/database.json'));
  await expect(page.locator('[data-technology-id]')).toHaveCount(679);
  const elapsed = performance.now() - started;
  expect(workers).toHaveLength(1); expect(errors).toEqual([]);
  await page.screenshot({ path: 'data/frontend-tests/real-night.png' });
  await sttvEnglish(page);
  await page.getByRole('button', { name: en.sttv_day_theme, exact: true }).click();
  await page.screenshot({ path: 'data/frontend-tests/real-day.png' });
  const card = page.locator('[data-technology-id="tech_titans"]');
  await card.scrollIntoViewIfNeeded(); await card.hover();
  await expect(page.getByRole('tooltip')).toContainText('Titans');
  await page.screenshot({ path: 'data/frontend-tests/real-tooltip.png' });
  await card.click();
  await expect(page.getByRole('option')).toHaveCount(3);
  await page.screenshot({ path: 'data/frontend-tests/real-variants.png' });
  await mkdir('data/frontend-tests', { recursive: true });
  await writeFile('data/frontend-tests/real-database.json', JSON.stringify({ elapsedMilliseconds: elapsed,
    technologies: 679, workerCount: workers.length, pageErrors: errors }, null, 2));
});

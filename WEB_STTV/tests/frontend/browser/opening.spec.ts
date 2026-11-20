import { test, expect } from '@playwright/test';
import { readFile, writeFile, mkdir, stat } from 'node:fs/promises';
import { resolve } from 'node:path';
import { sttvEnglish, sttvUpload, sttvUploadEntries, sttvReady, en, ru } from './helpers';
import { sttvDatabase, sttvTechnology, sttvSet } from '../fixtures';
import { sttvDatabaseKinds } from '../../../src/frontend/data/registry';

test('invalid JSON, retry, replacement, empty result, and diagnostic downloads', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  await sttvUploadEntries(page, [{ path: 'manifest.json', content: '{' }]);
  await expect(page.getByRole('status')).toHaveText(en.sttv_diagnostic_invalid_json);
  const downloading = page.waitForEvent('download');
  await page.getByRole('button', { name: en.sttv_save_report, exact: true }).click();
  const download = await downloading;
  const report = JSON.parse(await readFile((await download.path())!, 'utf8'));
  expect(report.error.code).toBe('invalid_json');
  expect(report.files[0]).toMatchObject({ name: 'manifest.json', size: 1 });
  expect(report.files).toHaveLength(1);
  expect(report.result).toBe('error'); expect(report.operationId).toBe(1);
  await page.getByRole('button', { name: en.sttv_retry, exact: true }).click();
  await expect(page.getByRole('status')).toHaveText(en.sttv_diagnostic_invalid_json);
  await sttvReady(page);
  await sttvUpload(page, sttvDatabase([]));
  await expect(page.getByRole('status')).toHaveText(en.sttv_dlc_tree_empty);
  await expect(page.locator('[data-technology-id]')).toHaveCount(0);
  await expect(page.getByRole('button', { name: en.sttv_retry, exact: true })).toHaveCount(0);
});
test('localization warnings stay in reports, conflicts block the replacement', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  const missing = sttvTechnology('tech_missing');
  missing.enrichments.localization.ru.name!.text = null;
  await sttvUpload(page, sttvDatabase([missing]));
  await expect(page.getByRole('status')).toHaveText(en.sttv_ready.replace('{count}', '1'));
  const downloading = page.waitForEvent('download');
  await page.getByRole('button', { name: en.sttv_save_report, exact: true }).click();
  const report = JSON.parse(await readFile((await (await downloading).path())!, 'utf8'));
  expect(report.diagnostics[0].code).toBe('missing_localization'); expect(report.error).toBeNull();
  const a = sttvTechnology('a'), b = sttvTechnology('b');
  b.enrichments.localization.ru.name!.requested_key = 'a';
  b.enrichments.localization.en.name!.requested_key = 'a';
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
test('real database loads in a worker and remains read-only', async ({ page, browser }) => {
  test.skip(!process.env.STTV_DATABASE_DIR, 'Requires the explicitly selected real dataset');
  test.setTimeout(900_000);
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  const workers: string[] = [];
  page.on('worker', worker => workers.push(worker.url()));
  await page.goto('/');
  const started = performance.now();
  const picking = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: ru.sttv_open_database, exact: true }).click();
  const directory = resolve(process.env.STTV_DATABASE_DIR!);
  const manifest = JSON.parse(await readFile(resolve(directory, 'manifest.json'), 'utf8'));
  const paths = Object.values(manifest.datasets).flatMap((dataset: any) => dataset.documents.map((row: any) => resolve(directory, row.path))) as string[];
  const sizes = await Promise.all(paths.map(async path => ({ path, bytes: (await stat(path)).size })));
  await (await picking).setFiles(directory);
  await expect(page.locator('[data-technology-id]')).toHaveCount(678, { timeout: 840_000 });
  const elapsed = performance.now() - started;
  expect(workers).toHaveLength(1); expect(errors).toEqual([]);
  await mkdir('data/frontend-stage5', { recursive: true });
  await page.screenshot({ path: 'data/frontend-stage5/real-ru-night.png' });
  const readReport = async () => {
    const downloading = page.waitForEvent('download');
    await page.getByRole('button', { name: /Save report|Сохранить отчёт/, exact: true }).click();
    return JSON.parse(await readFile((await (await downloading).path())!, 'utf8'));
  };
  const initialReport = await readReport();
  const positions = () => page.locator('[data-technology-id]').evaluateAll(cards => cards.map(card => ({
    id: card.getAttribute('data-technology-id'), area: card.closest('[data-area]')!.getAttribute('data-area'),
    row: card.parentElement!.dataset.row, column: card.parentElement!.dataset.tier,
  })));
  const initialPositions = await positions();
  expect(new Set(initialPositions.map(p => `${p.area}:${p.row}:${p.column}`)).size).toBe(678);
  await page.getByRole('button', { name: ru.sttv_day_theme, exact: true }).click();
  await page.screenshot({ path: 'data/frontend-stage5/real-ru-day.png' });
  expect(await positions()).toEqual(initialPositions);
  await sttvEnglish(page);
  const englishPositions = await positions(); expect(englishPositions).not.toEqual(initialPositions);
  expect(new Set(englishPositions.map(p => `${p.area}:${p.row}:${p.column}`)).size).toBe(678);
  await page.screenshot({ path: 'data/frontend-stage5/real-en-day.png' });
  await page.getByRole('button', { name: en.sttv_night_theme, exact: true }).click();
  await page.screenshot({ path: 'data/frontend-stage5/real-en-night.png' });
  expect(await positions()).toEqual(englishPositions);
  const card = page.locator('[data-technology-id="tech_titans"]');
  await card.scrollIntoViewIfNeeded(); await card.hover();
  await expect(page.getByRole('tooltip')).toContainText('Titans');
  await page.screenshot({ path: 'data/frontend-stage5/real-tooltip.png' });
  await card.click();
  await expect(page.getByRole('option')).toHaveCount(0);
  await expect(card.locator('button')).toHaveCount(0);
  expect(errors).toEqual([]);
  await mkdir('data/frontend-tests', { recursive: true });
  const memory = await page.evaluate(() => {
    const memory = (performance as unknown as { memory?: { usedJSHeapSize: number; totalJSHeapSize: number } }).memory;
    return memory ? { usedJSHeapSize: memory.usedJSHeapSize, totalJSHeapSize: memory.totalJSHeapSize } : null;
  });
  const report = { elapsedMilliseconds: elapsed, browser: browser.version(), files: sizes,
    totalBytes: sizes.reduce((total, file) => total + file.bytes, 0), maxFileBytes: Math.max(...sizes.map(file => file.bytes)),
    mainThreadMemory: memory, workerMemory: null,
    technologies: 678, workerCount: workers.length, pageErrors: errors };
  const downloading = page.waitForEvent('download');
  await page.getByRole('button', { name: en.sttv_save_report, exact: true }).click();
  const diagnostic = JSON.parse(await readFile((await (await downloading).path())!, 'utf8'));
  expect(diagnostic.coverage.documents.filter((row: any) => row.status === 'verified' && row.database !== 'technologies')).toHaveLength(0);
  expect(diagnostic.coverage.bytesRead).toBe(initialReport.coverage.bytesRead);
  expect(diagnostic.tree.combination.parameters).toEqual(initialReport.tree.combination.parameters);
  expect(diagnostic.tree.language).toBe('en');
  expect(diagnostic.tree.areas.reduce((sum: number, area: any) => sum + area.technologies, 0)).toBe(678);
  await writeFile('data/frontend-stage5/browser-real-set.json', JSON.stringify({ ...report,
    initialTree: initialReport.tree, tree: diagnostic.tree, coverage: diagnostic.coverage }, null, 2) + '\n');
});

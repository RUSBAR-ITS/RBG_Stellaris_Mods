import { test, expect } from '@playwright/test';
import { statSync, writeFileSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { sttvSet } from '../fixtures';
import { sttvEnglish, sttvReady, en } from './helpers';

test('large formatted JSON streams through the browser without File.text', async ({ page, browser }) => {
  test.skip(!process.env.STTV_LARGE_FILE, 'Requires an explicitly selected large JSON file');
  test.setTimeout(300_000);
  const path = resolve(process.env.STTV_LARGE_FILE!);
  await page.goto('/');
  await page.evaluate(() => {
    const input = document.createElement('input'); input.type = 'file'; input.id = 'large-probe'; document.body.append(input);
  });
  await page.locator('#large-probe').setInputFiles(path);
  const started = performance.now();
  const result = await page.locator('#large-probe').evaluate(async element => {
    const script = `import {sttvReadJson} from '${location.origin}/src/frontend/data/jsonStream.ts';
      onmessage=async ({data:file})=>{try {
        File.prototype.text=()=>{throw Error('File.text forbidden')};
        File.prototype.arrayBuffer=()=>{throw Error('File.arrayBuffer forbidden')};
        let count=0; const first=await sttvReadJson(file, ()=>{count++});
        postMessage({status:'success',count,expected:first.itemCount,hash:first.hash,bytes:first.bytes});
      } catch(e){postMessage({status:'failed',message:e.message})}}`;
    const url = URL.createObjectURL(new Blob([script], { type: 'text/javascript' }));
    const worker = new Worker(url, { type: 'module' });
    try {
      return await new Promise<Record<string, unknown>>((resolve, reject) => {
        worker.onmessage = event => resolve(event.data); worker.onerror = event => reject(new Error(event.message));
        worker.postMessage((element as HTMLInputElement).files![0]);
      });
    } finally { worker.terminate(); URL.revokeObjectURL(url); }
  });
  writeFileSync('data/stage17/large_stream_probe.json', JSON.stringify({ path, bytes: statSync(path).size,
    browser: browser.version(), seconds: (performance.now() - started) / 1000, ...result }, null, 2) + '\n');
  expect(result.status).toBe('success'); expect(result.count).toBe(result.expected); expect(result.count).toBeGreaterThan(0);
});

test('cancel terminates actual large-file streaming without publishing a previous catalog', async ({ page }) => {
  test.skip(!process.env.STTV_DATABASE_DIR, 'Requires an explicitly selected set directory');
  await page.goto('/'); await sttvEnglish(page); await sttvReady(page);
  await page.locator('input[type=file]').setInputFiles(resolve(process.env.STTV_DATABASE_DIR!));
  await expect(page.getByRole('button', { name: en.sttv_cancel, exact: true })).toBeVisible();
  await page.getByRole('button', { name: en.sttv_cancel, exact: true }).click();
  await expect(page.getByRole('status')).toHaveText(en.sttv_no_database);
  await expect(page.locator('[data-technology-id]')).toHaveCount(0);
  await sttvReady(page);
});

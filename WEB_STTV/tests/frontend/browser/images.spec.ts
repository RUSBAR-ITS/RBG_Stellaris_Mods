import { test, expect } from '@playwright/test';
import { readFile } from 'node:fs/promises';
import { sttvImageFixture, sttvPng } from '../imageFixture';
import { sttvUploadEntries, sttvEnglish, en } from './helpers';

test('shared images decode once, survive language changes, release on replacement and diagnose decode errors', async ({ page }) => {
  await page.addInitScript(() => {
    const counters = { created: 0, revoked: 0, decoded: 0 };
    Object.assign(window, { sttvImageCounters: counters });
    const create = URL.createObjectURL.bind(URL), revoke = URL.revokeObjectURL.bind(URL);
    URL.createObjectURL = blob => { counters.created++; return create(blob); };
    URL.revokeObjectURL = url => { counters.revoked++; revoke(url); };
    const decode = HTMLImageElement.prototype.decode;
    HTMLImageElement.prototype.decode = function () { counters.decoded++; return decode.call(this); };
  });
  await page.goto('/');
  await sttvUploadEntries(page, sttvImageFixture().entries);
  await expect(page.locator('.sttv-card-image img')).toHaveCount(3);
  const counts = () => page.evaluate(() => (window as any).sttvImageCounters);
  expect(await counts()).toEqual({ created: 1, revoked: 0, decoded: 1 });
  await sttvEnglish(page);
  await expect(page.locator('.sttv-card-image img')).toHaveCount(3);
  expect(await counts()).toEqual({ created: 1, revoked: 0, decoded: 1 });
  // Preserve the header/dimensions and valid content hash, but truncate the PNG payload.
  await sttvUploadEntries(page, sttvImageFixture(sttvPng.subarray(0, 24)).entries);
  await expect(page.locator('[data-technology-id]')).toHaveCount(3);
  await expect.poll(counts).toEqual({ created: 2, revoked: 1, decoded: 2 });
  await expect(page.locator('.sttv-card-image .sttv-image-placeholder')).toHaveCount(3);
  const download = page.waitForEvent('download');
  await page.getByRole('button', { name: en.sttv_save_report, exact: true }).click();
  const report = JSON.parse(await readFile((await (await download).path())!, 'utf8'));
  expect(report.diagnostics.filter((d: any) => d.code === 'image_unavailable')).toHaveLength(1);
  expect(report.diagnostics.find((d: any) => d.code === 'image_unavailable').details.reason).toBeTruthy();
});

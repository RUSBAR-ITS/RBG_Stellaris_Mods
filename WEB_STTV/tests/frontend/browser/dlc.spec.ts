import { sttvWorkPath } from '../../../frontend-workspace';
import { test, expect, type Page } from '@playwright/test';
import { resolve } from 'node:path';
import { readFile, mkdir } from 'node:fs/promises';
import { sttvEnglish, sttvUploadEntries, en, ru } from './helpers';
import { sttvDlcFixture } from '../dlcFixture';
import { sttvBundle } from '../manifestFixtures';

const button = (page: Page, name: string) => page.getByRole('button', { name, exact: true });
async function report(page: Page) {
  const pending = page.waitForEvent('download');
  await button(page, en.sttv_save_report).click();
  return JSON.parse(await readFile((await (await pending).path())!, 'utf8'));
}

test('draft, discard, failure, cancellation and a new snapshot preserve the correct tree', async ({ page }) => {
  const input = sttvDlcFixture(), original = sttvBundle(input), nextInput = structuredClone(input);
  const nodes = nextInput.find(d => d.database === 'technologies')!.items;
  Object.assign((nodes[0].enrichments!.technology_tree as any).reference_default,
    { children: [], visibility: { visible: false, reasons: [{ code: 'dlc_potential', pointer: '/value' }] } });
  Object.assign((nodes[1].enrichments!.technology_tree as any).reference_default, { parent_tech: null, status: 'root' });
  const next = sttvBundle(nextInput);
  next.manifest.snapshot_revision = 'f'.repeat(64);
  (next.manifest.technology_tree as any).combinations.reference_default.parameters.dlc.enabled = [];
  next.manifest.datasets.technologies.documents[0].source_hash = original.manifest.datasets.technologies.documents[0].source_hash;
  let mode = 'initial', submissions = 0, requests = 0, requestId = '';
  await page.context().route('**/api/sttv/**', async route => {
    const path = new URL(route.request().url()).pathname;
    requests++;
    if (path.endsWith('/connect')) return route.fulfill({ json: { token: 'test' } });
    if (path.endsWith('/operations')) requestId = route.request().postDataJSON().requestId;
    const job = { id: 'job', requestId, before: original.manifest.snapshot_revision, error: null,
      status: 'completed', result: { setId: original.manifest.set_id, snapshotRevision: mode === 'success' ? next.manifest.snapshot_revision : original.manifest.snapshot_revision,
        combinationId: 'reference_default', profile: { known: ['a', 'b'], enabled: mode === 'success' ? [] : ['a', 'b'] }, diagnostics: [] } };
    if (path.endsWith('/operations')) {
      submissions++;
      if (mode === 'fail') return route.fulfill({ json: { ...job, status: 'failed', result: null, error: { code: 'test_failure', message: 'Injected' } } });
      if (mode === 'cancel') return route.fulfill({ json: { ...job, status: 'running', result: null } });
      return route.fulfill({ json: job });
    }
    if (path.endsWith('/cancel')) mode = 'cancelled';
    if (path.includes('/operations/job')) return route.fulfill({ json: { ...job,
      status: mode === 'cancelled' ? 'cancelled' : 'running', result: null, error: { code: 'cancelled', message: 'Cancelled' } } });
    const bundle = mode === 'success' ? next : original;
    if (path.endsWith('/manifest')) return route.fulfill({ json: bundle.manifest });
    const id = path.split('/').at(-1), kind = path.split('/').at(-2)!;
    const row = bundle.manifest.datasets[kind as keyof typeof bundle.manifest.datasets].documents.find(d => d.document_id === id)!;
    return route.fulfill({ body: bundle.entries.find(e => e.path === row.path)!.content, contentType: 'application/json' });
  });
  await page.goto('/'); await sttvEnglish(page);
  await sttvUploadEntries(page, original.entries);
  await expect(page.locator('[data-technology-id]')).toHaveCount(2);
  await expect(page.locator('[data-connection-child]')).toHaveCount(1);
  await button(page, en.sttv_nav_dlc).click();
  await expect(page.getByRole('switch')).toHaveCount(2);
  await page.getByRole('switch').first().focus(); await page.keyboard.press('Space');
  await expect(page.getByRole('switch').first()).toHaveAttribute('aria-checked', 'false');
  expect(submissions).toBe(1);
  await button(page, en.sttv_dlc_discard).click();
  await expect(page.getByRole('switch').first()).toHaveAttribute('aria-checked', 'true');
  for (const toggle of await page.getByRole('switch').all()) await toggle.click();
  await button(page, en.sttv_nav_tree).click();
  await expect(page.getByRole('status').last()).toHaveText(en.sttv_dlc_pending);
  await expect(page.locator('[data-technology-id]')).toHaveCount(2);
  await button(page, en.sttv_nav_dlc).click();
  mode = 'fail'; await button(page, en.sttv_dlc_apply).click();
  await expect(page.getByRole('status').last()).toHaveText(en.sttv_dlc_apply_failed);
  await expect(page.locator('[data-technology-id]')).toHaveCount(2);
  mode = 'cancel'; await button(page, en.sttv_dlc_apply).click();
  await button(page, en.sttv_cancel).click();
  await expect(page.getByRole('status').last()).toHaveText(en.sttv_dlc_cancelled);
  await expect(page.locator('[data-technology-id]')).toHaveCount(2);
  mode = 'success'; await button(page, en.sttv_dlc_apply).click();
  await expect(page.locator('[data-technology-id]')).toHaveCount(1);
  await expect(page.locator('[data-connection-child]')).toHaveCount(0);
  expect(submissions).toBe(4);
  expect((await report(page)).snapshotRevision).toBe(next.manifest.snapshot_revision);
  requests = 0; await page.reload();
  await expect(page.locator('[data-technology-id]')).toHaveCount(0);
  expect(requests).toBe(0);
});

test('real catalog thumbnails, navigation and DLC profiles agree with Python', async ({ page }) => {
  test.skip(!process.env.STTV_DATABASE_DIR, 'Requires the registered prepared set and local service');
  test.setTimeout(180000);
  await mkdir(sttvWorkPath('stage20/screenshots'), { recursive: true });
  await page.goto('/'); await sttvEnglish(page);
  await page.locator('input[type=file]').setInputFiles(resolve(process.env.STTV_DATABASE_DIR!));
  await expect(page.locator('[data-technology-id]')).toHaveCount(678, { timeout: 90000 });
  await button(page, en.sttv_nav_dlc).click();
  await expect(page.getByRole('switch')).toHaveCount(36);
  await expect(page.locator('.sttv-dlc-image img')).toHaveCount(32);
  await expect(button(page, en.sttv_dlc_apply)).toBeDisabled();
  await page.screenshot({ path: sttvWorkPath('stage20/screenshots/dlc-night-en.png') });
  await button(page, en.sttv_day_theme).click();
  await button(page, en.sttv_language).click(); await page.getByRole('option', { name: 'Русский', exact: true }).click();
  await page.screenshot({ path: sttvWorkPath('stage20/screenshots/dlc-day-ru.png') });
  await sttvEnglish(page);
  for (const toggle of await page.getByRole('switch').all()) await toggle.click();
  await button(page, en.sttv_dlc_apply).click();
  await expect(page.locator('[data-technology-id]')).toHaveCount(543, { timeout: 90000 });
  const result = await report(page);
  expect(result.dlc.profile.enabled).toEqual([]);
  expect(result.dlc.counts.visible).toBe(543);
  expect(result.dlc.counts.hidden).toBe(136);
  expect(result.service.available).toBe(true);
  expect(result.coverage.verifiedDocuments).toBe(68);
  await button(page, en.sttv_nav_tree).click();
  await expect(page.locator('[data-technology-id="tech_archeology_lab"]')).toHaveCount(1);
  await page.screenshot({ path: sttvWorkPath('stage20/screenshots/tree-no-dlc.png') });
  await button(page, en.sttv_nav_dlc).click();
  for (const toggle of await page.getByRole('switch').all()) await toggle.click();
  await button(page, en.sttv_dlc_apply).click();
  await expect(page.locator('[data-technology-id]')).toHaveCount(678, { timeout: 60000 });
  await expect(page.locator('[data-technology-id="tech_archeology_lab"]')).toHaveCount(0);
  await button(page, en.sttv_nav_tree).click();
  await expect(page.locator('[data-technology-id]')).toHaveCount(678);
});

test('offline prepared profiles remain viewable and an all-hidden result is a valid empty tree', async ({ page }) => {
  await page.context().route('**/api/sttv/**', route => route.abort());
  await page.goto('/'); await sttvEnglish(page);
  const input = sttvDlcFixture();
  await sttvUploadEntries(page, sttvBundle(input).entries);
  await expect(page.locator('[data-technology-id]')).toHaveCount(2);
  await button(page, en.sttv_nav_dlc).click();
  await expect(page.getByRole('switch')).toHaveCount(2);
  await expect(page.getByText(en.sttv_dlc_service_unavailable)).toBeVisible();
  await page.getByRole('switch').first().click();
  await expect(button(page, en.sttv_dlc_apply)).toBeDisabled();
  const nodes = input.find(d => d.database === 'technologies')!.items;
  for (const node of nodes) Object.assign((node.enrichments!.technology_tree as any).reference_default,
    { parent_tech: null, children: [], status: 'root', visibility: { visible: false, reasons: [] } });
  await button(page, en.sttv_nav_tree).click();
  await sttvUploadEntries(page, sttvBundle(input).entries);
  await expect(page.getByRole('status').last()).toHaveText(en.sttv_dlc_tree_empty);
  await expect(page.locator('[data-technology-id]')).toHaveCount(0);
  await button(page, en.sttv_nav_dlc).click();
  await expect(page.getByRole('switch')).toHaveCount(2);
});

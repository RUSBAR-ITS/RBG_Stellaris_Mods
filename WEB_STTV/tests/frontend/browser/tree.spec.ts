import { test, expect } from '@playwright/test';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { sttvEnglish, sttvUpload, sttvUploadEntries, en } from './helpers';
import { sttvDatabase, sttvTechnology, sttvSet } from '../fixtures';
import { sttvConnect } from '../treeFixtures';
import { sttvBundle } from '../manifestFixtures';

test('tree geometry follows saved links in DOM order and does not reserve a blank level-zero column', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  const nodes = [sttvTechnology('A1', 0), sttvTechnology('A2', 0), sttvTechnology('A3', 1),
    sttvTechnology('B', 1), sttvTechnology('C', 2), sttvTechnology('D', 1)];
  sttvConnect(nodes, { A2: 'A1', A3: 'A2', B: 'A1', C: 'B', D: 'C' });
  await sttvUpload(page, sttvDatabase(nodes));
  const cards = page.locator('[data-technology-id]'); await expect(cards).toHaveCount(6);
  const positions = await cards.evaluateAll(elements => elements.map(card => {
    const rect = card.getBoundingClientRect();
    return { id: card.getAttribute('data-technology-id'), row: Number(card.parentElement!.dataset.row),
      column: Number(card.parentElement!.dataset.tier), x: rect.x, y: rect.y, width: rect.width, height: rect.height };
  }));
  expect(positions.map(({ id, row, column }) => ({ id, row, column }))).toEqual([
    { id: 'A1', row: 0, column: 0 }, { id: 'A2', row: 1, column: 0 }, { id: 'A3', row: 1, column: 1 },
    { id: 'B', row: 2, column: 1 }, { id: 'C', row: 2, column: 2 }, { id: 'D', row: 3, column: 1 },
  ]);
  for (let a = 0; a < positions.length; a++) for (let b = a + 1; b < positions.length; b++) {
    const first = positions[a], second = positions[b];
    expect(first.x + first.width <= second.x || second.x + second.width <= first.x
      || first.y + first.height <= second.y || second.y + second.height <= first.y).toBe(true);
  }
  const field = (await page.locator('.sttv-technology-field').boundingBox())!;
  expect(positions[0].x - field.x).toBe(6);
  await cards.nth(0).focus(); await page.keyboard.press('Tab'); await expect(cards.nth(1)).toBeFocused();
  await page.keyboard.press('Tab'); await expect(cards.nth(2)).toBeFocused();
});

test('missing, stale and malformed saved combinations show distinct reportable errors', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  for (const [mode, message] of [
    ['missing', en.sttv_diagnostic_tree_combination_missing],
    ['stale', en.sttv_diagnostic_tree_combination_stale],
    ['record', en.sttv_diagnostic_tree_enrichment_invalid],
  ]) {
    const node = sttvTechnology('a');
    if (mode === 'record') node.enrichments.technology_tree = {} as any;
    const bundle = sttvBundle(sttvSet(sttvDatabase([node])));
    const metadata = bundle.manifest.technology_tree as any;
    if (mode === 'missing') delete metadata.combinations.reference_default;
    if (mode === 'stale') metadata.combinations.reference_default.inputs[0].hash = '9'.repeat(64);
    bundle.entries.find(row => row.path === 'manifest.json')!.content = JSON.stringify(bundle.manifest);
    await sttvUploadEntries(page, bundle.entries);
    await expect(page.getByRole('status')).toHaveText(message);
    await expect(page.locator('[data-technology-id]')).toHaveCount(0);
    const downloading = page.waitForEvent('download');
    await page.getByRole('button', { name: en.sttv_save_report, exact: true }).click();
    const report = JSON.parse(await readFile((await (await downloading).path())!, 'utf8'));
    expect(report.error.details.reason).toBeTruthy();
  }
});

test('another prepared combination is opened through its configuration and preserves its variants', async ({ page }) => {
  test.skip(!process.env.STTV_DATABASE_DIR || process.env.STTV_PREVIEW === '1', 'Requires real files and the development config module');
  await page.route('**/config/frontend/tree_layout.json*', async route => {
    const response = await route.fetch();
    await route.fulfill({ response, body: (await response.text()).replaceAll('reference_default', 'reference_variants') });
  });
  await page.goto('/'); await sttvEnglish(page);
  await page.locator('input[type=file]').setInputFiles(resolve(process.env.STTV_DATABASE_DIR!));
  await expect(page.locator('[data-technology-id]')).toHaveCount(679, { timeout: 60000 });
  await expect(page.locator('[data-connection-child]')).toHaveCount(463);
  await expect(page.locator('[data-area="society"] [data-technology-id]')).toHaveCount(319);
  await expect(page.locator('[data-area="engineering"] [data-technology-id]')).toHaveCount(192);
  await expect(page.locator('[data-technology-id] button')).toHaveCount(0);
  const downloading = page.waitForEvent('download');
  await page.getByRole('button', { name: en.sttv_save_report, exact: true }).click();
  const report = JSON.parse(await readFile((await (await downloading).path())!, 'utf8'));
  expect(report.tree.combination.id).toBe('reference_variants');
  expect(report.tree.settings.combination_id).toBe('reference_variants');
  expect(report.tree.hiddenCrossAreaLinks).toBe(38);
  expect(report.tree.connections.logicalConnections).toBe(463);
  expect(report.coverage.verifiedDocuments).toBe(35);
});

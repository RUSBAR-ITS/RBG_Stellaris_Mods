import { test, expect } from '@playwright/test';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { sttvDatabase, sttvTechnology } from '../fixtures';
import { sttvConnect } from '../treeFixtures';
import { sttvEnglish, sttvUpload, en, ru } from './helpers';

test('card hover colors complete parent/child paths without rerouting or changing sibling branches', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  const nodes = Object.entries({ P: 0, A: 1, B: 2, C: 1, D: 2, E: 1 }).map(([id, tier]) => sttvTechnology(id, tier));
  sttvConnect(nodes, { A: 'P', B: 'A', C: 'A', D: 'C', E: 'A' });
  await sttvUpload(page, sttvDatabase(nodes));
  await expect(page.locator('[data-connection-child]')).toHaveCount(5);
  const paths = () => page.locator('[data-connection-segment]').evaluateAll(nodes => nodes.map(n => n.getAttribute('d')));
  const before = await paths();
  const card = page.locator('[data-technology-id="C"]'); await card.hover();
  await expect(page.getByRole('tooltip')).toBeVisible();
  const colors = await page.locator('[data-connection-segment]').evaluateAll(nodes => nodes.map(node => ({
    parent: node.getAttribute('data-parent'), children: JSON.parse(node.getAttribute('data-children')!),
    role: node.getAttribute('data-role'), color: getComputedStyle(node).stroke,
  })));
  for (const line of colors) expect(line.role).toBe(line.parent === 'C' ? 'children' : line.children.includes('C') ? 'parent' : 'default');
  expect(colors.find(v => v.role === 'parent')!.color).not.toBe(colors.find(v => v.role === 'children')!.color);
  expect(colors.some(v => v.parent === 'A' && v.children.includes('C') && v.children.includes('E') && v.role === 'parent')).toBe(true);
  expect(colors.some(v => v.children.includes('E') && !v.children.includes('C') && v.role === 'default')).toBe(true);
  await page.mouse.move(5, 5);
  await expect(page.locator('.sttv-connections [data-role="parent"], .sttv-connections [data-role="children"]')).toHaveCount(0);
  expect(await paths()).toEqual(before);
  await page.getByRole('button', { name: en.sttv_day_theme, exact: true }).click();
  await card.hover();
  await expect(page.locator('.sttv-connection[data-role="parent"]').first()).toHaveCSS('stroke', 'rgb(23, 104, 166)');
  expect(await paths()).toEqual(before);
  mkdirSync('data/frontend-stage7', { recursive: true });
  await page.screenshot({ path: 'data/frontend-stage7/synthetic-day.png' });
});

test('connection endpoints stay on cards through scrolling, menu changes and window resizing', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  const nodes = [sttvTechnology('A', 0), sttvTechnology('B', 4), sttvTechnology('C', 0), sttvTechnology('D', 2)];
  sttvConnect(nodes, { B: 'A', C: 'B', D: 'C' });
  await sttvUpload(page, sttvDatabase(nodes));
  await expect(page.locator('[data-connection-child]')).toHaveCount(3);
  mkdirSync('data/frontend-stage7', { recursive: true });
  await page.screenshot({ path: 'data/frontend-stage7/reverse-night.png' });
  const check = async () => {
    const endpoints = await page.locator('[data-connection-child]').evaluateAll(arrows => arrows.map(arrow => {
      const child = document.querySelector(`[data-technology-id="${arrow.getAttribute('data-connection-child')}"]`)!;
      const card = child.getBoundingClientRect();
      const [x, y] = arrow.getAttribute('d')!.slice(1).split('L')[0].split(',').map(Number);
      const { x: px, y: py } = new DOMPoint(x, y).matrixTransform((arrow as SVGGraphicsElement).getScreenCTM()!);
      return Math.min(Math.hypot(px - card.left, py - (card.top + card.height / 2)),
        Math.hypot(px - card.right, py - (card.top + card.height / 2)),
        Math.hypot(px - (card.left + card.width / 2), py - card.top));
    }));
    for (const distance of endpoints) expect(distance).toBeLessThan(0.1);
  };
  await check();
  await page.locator('#sttv-viewport-content').evaluate(e => { e.scrollLeft = 300; e.scrollTop = 60; });
  await check();
  await page.getByRole('button', { name: en.sttv_collapse_menu, exact: true }).click();
  await page.setViewportSize({ width: 1000, height: 650 }); await check();
});

test('routing failure is localized and exports its combination and configuration', async ({ page }) => {
  test.skip(process.env.STTV_PREVIEW === '1', 'Uses the development configuration module');
  await page.route('**/config/frontend/connections.json*', async route => {
    const response = await route.fetch();
    await route.fulfill({ response, body: (await response.text()).replaceAll('16', '0') });
  });
  await page.goto('/'); await sttvEnglish(page);
  const nodes = [sttvTechnology('A'), sttvTechnology('B', 4)]; sttvConnect(nodes, { B: 'A' });
  await sttvUpload(page, sttvDatabase(nodes));
  await expect(page.getByRole('status')).toHaveText(en.sttv_diagnostic_tree_connections_failed);
  await expect(page.locator('[data-technology-id]')).toHaveCount(0);
  const download = page.waitForEvent('download'); await page.getByRole('button', { name: en.sttv_save_report, exact: true }).click();
  const report = JSON.parse(readFileSync((await (await download).path())!, 'utf8'));
  expect(report.error.details.combination.id).toBe('reference_default');
  expect(report.error.details.routingSettings.maxLaneAttempts).toBe(0);
  expect(report.error.details.language).toBe('en');
});

test('real connections cover all local parents and retain geometry while hovering in both themes', async ({ page }) => {
  test.skip(!process.env.STTV_DATABASE_DIR, 'Requires the prepared manifest dataset');
  mkdirSync('data/frontend-stage7', { recursive: true });
  await page.goto('/');
  await page.locator('input[type=file]').setInputFiles(resolve(process.env.STTV_DATABASE_DIR!));
  await expect(page.locator('[data-connection-child]')).toHaveCount(464, { timeout: 60000 });
  const firstPaths = await page.locator('[data-connection-segment]').evaluateAll(nodes => nodes.map(n => n.getAttribute('d')));
  const card = page.locator('[data-technology-id="tech_lasers_3"]');
  await card.scrollIntoViewIfNeeded(); await card.hover();
  await page.screenshot({ path: 'data/frontend-stage7/real-ru-night.png' });
  await expect(page.locator('.sttv-connection[data-role="parent"]').first()).toHaveCSS('stroke', 'rgb(115, 191, 255)');
  await expect(page.locator('.sttv-connection[data-role="children"]').first()).toHaveCSS('stroke', 'rgb(242, 179, 102)');
  await page.getByRole('button', { name: ru.sttv_day_theme, exact: true }).click();
  await card.hover(); await page.screenshot({ path: 'data/frontend-stage7/real-ru-day.png' });
  expect(await page.locator('[data-connection-segment]').evaluateAll(nodes => nodes.map(n => n.getAttribute('d')))).toEqual(firstPaths);
  await sttvEnglish(page);
  await expect(page.locator('[data-connection-child]')).toHaveCount(464);
  await card.scrollIntoViewIfNeeded(); await card.hover();
  await page.screenshot({ path: 'data/frontend-stage7/real-en-day.png' });
  await page.getByRole('button', { name: en.sttv_night_theme, exact: true }).click();
  await card.hover(); await page.screenshot({ path: 'data/frontend-stage7/real-en-night.png' });
  const download = page.waitForEvent('download'); await page.getByRole('button', { name: en.sttv_save_report, exact: true }).click();
  const report = JSON.parse(readFileSync((await (await download).path())!, 'utf8'));
  expect(report.tree.connections.logicalConnections).toBe(464); expect(report.coverage.verifiedDocuments).toBe(35);
  writeFileSync('data/frontend-stage7/browser-real-set.json', JSON.stringify(report, null, 2));
});

import { test, expect } from '@playwright/test';
import { mkdirSync } from 'node:fs';
import { sttvDatabase, sttvTechnology } from '../fixtures';
import { sttvConnect } from '../treeFixtures';
import { sttvEnglish, sttvUpload, en, ru } from './helpers';
import { sttvZoom, sttvZoomGeometry, sttvCheckConnectionAnchors } from './zoomHelpers';

test('zoom is available before opening and remains session state across menu, language, theme and set changes', async ({ page }) => {
  await page.goto('/');
  const zoom = () => page.locator('.sttv-zoom-selector').getByRole('button');
  await expect(zoom()).toHaveText('50%');
  await zoom().press('ArrowDown');
  await expect(page.getByRole('option')).toHaveText(['50%', '75%', '100%', '125%', '150%']);
  await page.getByRole('listbox').press('ArrowDown'); await page.getByRole('listbox').press('Enter');
  await expect(zoom()).toHaveText('75%');
  await sttvEnglish(page); await expect(zoom()).toHaveAccessibleName(en.sttv_zoom);
  await sttvUpload(page, sttvDatabase([sttvTechnology('first')]));
  await expect(page.locator('[data-technology-id]')).toHaveCount(1);
  expect((await sttvZoomGeometry(page)).cardWidth).toBe(390);
  await page.getByRole('button', { name: en.sttv_day_theme, exact: true }).click();
  await page.getByRole('button', { name: en.sttv_collapse_menu, exact: true }).click();
  await expect(zoom()).toHaveCount(0);
  await page.getByRole('button', { name: en.sttv_expand_menu, exact: true }).click();
  await expect(zoom()).toHaveText('75%');
  await sttvUpload(page, sttvDatabase([sttvTechnology('second')]));
  await expect(page.locator('[data-technology-id="second"]')).toBeVisible();
  await expect(zoom()).toHaveText('75%');
  await page.getByRole('button', { name: en.sttv_language, exact: true }).click();
  await page.getByRole('option', { name: ru.sttv_language_ru, exact: true }).click();
  await expect(zoom()).toHaveAccessibleName(ru.sttv_zoom); await expect(zoom()).toHaveText('75%');
  await page.reload(); await expect(zoom()).toHaveText('50%');
  await expect(page.locator('[data-technology-id]')).toHaveCount(0);
});

test('all zoom levels preserve geometry and centre, clamp scroll bounds and leave menu dimensions unchanged', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  const nodes = Array.from({ length: 36 }, (_, i) => sttvTechnology(`zoom_${i}`, i % 7));
  sttvConnect(nodes, { zoom_1: 'zoom_0', zoom_2: 'zoom_1' });
  for (const language of ['ru', 'en'] as const) {
    nodes[0].enrichments.localization[language].name!.text = 'A complete and very long technology name with many additional words '.repeat(3);
  }
  await sttvUpload(page, sttvDatabase(nodes)); await expect(page.locator('[data-technology-id]')).toHaveCount(36);
  const menu = (await page.locator('.sttv-menu-panel').boundingBox())!;
  const paths = await page.locator('[data-connection-segment]').evaluateAll(nodes => nodes.map(n => n.getAttribute('d')));
  await page.locator('#sttv-viewport-content').evaluate(e => { e.scrollLeft = 300; e.scrollTop = 800; });
  for (const percent of [75, 100, 125, 150, 50]) {
    const before = await sttvZoomGeometry(page);
    await sttvZoom(page, percent);
    const after = await sttvZoomGeometry(page);
    const expectedX = Math.max(0, Math.min((before.x + before.width / 2) / before.scale * after.scale - after.width / 2,
      after.scrollWidth - after.width));
    const expectedY = Math.max(0, Math.min((before.y + before.height / 2) / before.scale * after.scale - after.height / 2,
      after.scrollHeight - after.height));
    expect(Math.abs(after.x - expectedX)).toBeLessThanOrEqual(1);
    expect(Math.abs(after.y - expectedY)).toBeLessThanOrEqual(1);
    expect(after.cardWidth).toBe(520 * percent / 100);
    expect(after.cardHeight).toBeCloseTo(after.baseHeight * percent / 100, 1);
    expect(after.titleHeight).toBeCloseTo(after.titleBaseHeight * percent / 100, 1);
    expect(Math.abs(after.scrollWidth - Math.max(after.width, after.fieldWidth))).toBeLessThanOrEqual(1);
    expect(Math.abs(after.scrollHeight - Math.max(after.height, after.fieldHeight))).toBeLessThanOrEqual(1);
    expect((await page.locator('.sttv-menu-panel').boundingBox())!.width).toBe(menu.width);
    expect(await page.locator('[data-connection-segment]').evaluateAll(nodes => nodes.map(n => n.getAttribute('d')))).toEqual(paths);
    await sttvCheckConnectionAnchors(page);
  }
  await page.locator('#sttv-viewport-content').evaluate(e => { e.scrollLeft = e.scrollWidth; e.scrollTop = e.scrollHeight; });
  const end = await sttvZoomGeometry(page);
  expect(end.x).toBe(end.scrollWidth - end.width); expect(end.y).toBe(end.scrollHeight - end.height);
  await sttvZoom(page, 150); await sttvZoom(page, 50);
  const clamped = await sttvZoomGeometry(page);
  expect(clamped.x).toBeLessThanOrEqual(clamped.scrollWidth - clamped.width);
  expect(clamped.y).toBeLessThanOrEqual(clamped.scrollHeight - clamped.height);
  mkdirSync('data/frontend-stage9', { recursive: true });
  await page.locator('#sttv-viewport-content').evaluate(e => { e.scrollLeft = 0; e.scrollTop = 0; });
  await page.screenshot({ path: 'data/frontend-stage9/long-title-50.png' });
});

test('scrollbars appear only for scaled bounds and keyboard focus reaches clipped distant cards', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  await sttvUpload(page, sttvDatabase([sttvTechnology('small_0', 0), sttvTechnology('small_1', 1)]));
  await expect(page.locator('[data-technology-id]')).toHaveCount(2);
  await expect(page.getByRole('scrollbar')).toHaveCount(0);
  await sttvZoom(page, 150);
  await expect(page.getByRole('scrollbar', { name: en.sttv_horizontal_scroll })).toBeVisible();
  await page.locator('[data-technology-id="small_0"]').focus(); await page.keyboard.press('Tab');
  const last = page.locator('[data-technology-id="small_1"]');
  await expect(last).toBeFocused(); await expect(last).toBeInViewport();
  await sttvZoom(page, 50); await expect(page.getByRole('scrollbar')).toHaveCount(0);
});

test('tooltips retain size and close on zoom, while focus and relationship highlighting work at every scale', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  const nodes = ['a', 'b', 'c'].map((id, tier) => sttvTechnology(id, tier));
  sttvConnect(nodes, { b: 'a', c: 'b' }); await sttvUpload(page, sttvDatabase(nodes));
  const card = page.locator('[data-technology-id="b"]'); await expect(card).toBeVisible();
  let tooltipWidth = 0;
  for (const percent of [50, 100, 150]) {
    await sttvZoom(page, percent); await expect(page.getByRole('tooltip')).toHaveCount(0);
    await card.hover(); await expect(page.getByRole('tooltip')).toBeVisible();
    const tooltip = (await page.getByRole('tooltip').boundingBox())!;
    if (tooltipWidth) expect(tooltip.width).toBe(tooltipWidth); else tooltipWidth = tooltip.width;
    expect(tooltip.x).toBeGreaterThanOrEqual(0); expect(tooltip.x + tooltip.width).toBeLessThanOrEqual(1440);
    await expect(page.locator('.sttv-connection[data-role="parent"]').first()).toBeAttached();
    await expect(page.locator('.sttv-connection[data-role="children"]').first()).toBeAttached();
    await sttvCheckConnectionAnchors(page);
    await page.mouse.move(0, 0); await card.focus(); await expect(page.getByRole('tooltip')).toBeVisible();
    await page.keyboard.press('Tab'); await expect(page.locator('[data-technology-id="c"]')).toBeFocused();
    await expect(page.locator('[data-technology-id="c"]')).toBeInViewport();
  }
});

test('real set keeps every image, full title and connection across zoom and language changes', async ({ page }) => {
  test.skip(!process.env.STTV_DATABASE_DIR, 'Requires the prepared set'); test.setTimeout(120000);
  await page.goto('/'); await page.locator('input[type=file]').setInputFiles(process.env.STTV_DATABASE_DIR!);
  await expect(page.locator('[data-technology-id]')).toHaveCount(679, { timeout: 90000 });
  await expect(page.locator('[data-connection-child]')).toHaveCount(464);
  mkdirSync('data/frontend-stage9', { recursive: true });
  for (const language of ['ru', 'en']) {
    if (language === 'en') await sttvEnglish(page);
    for (const percent of [50, 100, 150]) {
      await sttvZoom(page, percent); await sttvCheckConnectionAnchors(page);
      expect(await page.locator('.sttv-card-title').evaluateAll(items => items.every(item => item.scrollWidth <= item.clientWidth + 1))).toBe(true);
      await page.locator('#sttv-viewport-content').evaluate(e => { e.scrollLeft = 0; e.scrollTop = 0; });
      await page.screenshot({ path: `data/frontend-stage9/real-${language}-${percent}.png` });
    }
  }
});

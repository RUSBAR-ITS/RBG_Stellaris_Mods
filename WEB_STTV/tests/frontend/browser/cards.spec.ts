import { sttvWorkPath } from '../../../frontend-workspace';
import { test, expect } from '@playwright/test';
import { mkdirSync } from 'node:fs';
import { sttvDatabase, sttvTechnology, sttvAssignment as a, sttvScalar as s, sttvBlock as b } from '../fixtures';
import { sttvUpload, sttvEnglish, en } from './helpers';

test('expanded cards preserve full names, hide absent values, show zero and distinguish rarity in both themes', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  const nodes = ['physics', 'society', 'engineering'].map((area, i) => sttvTechnology(`card_${i}`, i, area as any));
  const long = 'A complete technology title with many words and an exceptionally long unbroken identifier '.repeat(3);
  for (const language of ['ru', 'en'] as const) nodes[0].enrichments.localization[language].name!.text = long;
  nodes[0].value!.items!.push(a('cost', s('0')), a('weight', s('0')), a('is_rare', s('yes')),
    a('is_dangerous', s('yes')), a('start_tech', s('yes')), a('levels', s('5')));
  nodes[1].value!.items!.push(a('is_rare', s('yes')), a('levels', s('-1')));
  nodes[2].value!.items!.push(a('cost', b([a('factor', s('2500')), a('modifier', b([a('factor', s('0'))]))])));
  await sttvUpload(page, sttvDatabase(nodes));
  const cards = page.locator('[data-technology-id]'); await expect(cards).toHaveCount(3);
  const first = page.locator('[data-technology-id="card_0"]'), second = page.locator('[data-technology-id="card_1"]');
  await expect(first.locator('.sttv-card-title')).toHaveText(long.trim());
  await expect(first).toHaveAttribute('data-rarity', 'dangerous');
  await expect(first).toContainText(/Cost:.*0/); await expect(first).toContainText('Weight: 0');
  await expect(first).toContainText('Levels: 5'); await expect(first).toContainText('Starting');
  await expect(second.locator('.sttv-card-attribute')).toHaveCount(0);
  const geometry = await cards.evaluateAll(cards => cards.map(card => ({ height: card.getBoundingClientRect().height,
    content: [...card.querySelectorAll('.sttv-card-details, .sttv-card-title')].map(e => [e.className, e.scrollWidth, e.clientWidth, e.scrollHeight, e.clientHeight]),
    overflow: [...card.querySelectorAll('.sttv-card-details, .sttv-card-title')].some(e => e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1),
    background: getComputedStyle(card).backgroundColor, border: getComputedStyle(card).borderColor,
    surface: getComputedStyle(card.querySelector('.sttv-card-content')!).backgroundColor })));
  expect(new Set(geometry.map(g => g.height)).size).toBe(1); expect(geometry.every(g => !g.overflow), JSON.stringify(geometry)).toBe(true);
  expect(new Set(geometry.map(g => g.surface)).size).toBe(3);
  expect(geometry.every(g => g.background === g.border)).toBe(true);
  expect(geometry[0].background).not.toBe(geometry[0].surface);
  expect(geometry[1].background).not.toBe(geometry[1].surface);
  expect(geometry[2].background).toBe(geometry[2].surface);
  expect(geometry[0].border).not.toBe(geometry[1].border);
  mkdirSync(sttvWorkPath('frontend-stage8'), { recursive: true });
  await first.scrollIntoViewIfNeeded(); await page.screenshot({ path: sttvWorkPath('frontend-stage8/synthetic-night.png') });
  await page.getByRole('button', { name: en.sttv_day_theme, exact: true }).click();
  expect(await first.evaluate(e => getComputedStyle(e).backgroundColor)).not.toBe(geometry[0].background);
  await page.screenshot({ path: sttvWorkPath('frontend-stage8/synthetic-day.png') });
});

test('real prepared images and card geometry load without game paths in RU and EN', async ({ page }) => {
  test.skip(!process.env.STTV_DATABASE_DIR, 'Requires an explicitly selected real set');
  test.setTimeout(120000);
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/'); await page.locator('input[type=file]').setInputFiles(process.env.STTV_DATABASE_DIR!);
  const cards = page.locator('[data-technology-id]'); await expect(cards).toHaveCount(678, { timeout: 90000 });
  await expect.poll(() => cards.locator('.sttv-card-image img').evaluateAll(images =>
    images.filter(image => (image as HTMLImageElement).complete && (image as HTMLImageElement).naturalWidth > 0).length)).toBe(678);
  for (const language of ['ru', 'en']) {
    if (language === 'en') await sttvEnglish(page);
    await expect(cards).toHaveCount(678);
    expect(await cards.evaluateAll(cards => cards.every(card => [...card.querySelectorAll('.sttv-card-details, .sttv-card-title')]
      .every(e => e.scrollWidth <= e.clientWidth + 1 && e.scrollHeight <= e.clientHeight + 1)))).toBe(true);
    mkdirSync(sttvWorkPath('frontend-stage8'), { recursive: true });
    await page.screenshot({ path: sttvWorkPath(`frontend-stage8/real-${language}-night.png`) });
  }
  expect(errors).toEqual([]);
});

import { test, expect } from '@playwright/test';
import { openTree, technology, sttvEnglish, en } from './helpers';

test('expanded cards preserve full names, hide absent values, show zero and distinguish rarity in both themes', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  const nodes = ['physics', 'society', 'engineering'].map((area, i) => technology(`card_${i}`, i, area));
  const long = 'A complete technology title with many words and an exceptionally long unbroken identifier '.repeat(3);
  Object.assign(nodes[0], { name: long, cost: 0, weight: 0, rare: true, dangerous: true, starting: true, levels: 5 });
  Object.assign(nodes[1], { rare: true, levels: -1 });
  await openTree(page, nodes);
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
  await page.getByRole('button', { name: en.sttv_day_theme, exact: true }).click();
  expect(await first.evaluate(e => getComputedStyle(e).backgroundColor)).not.toBe(geometry[0].background);
});


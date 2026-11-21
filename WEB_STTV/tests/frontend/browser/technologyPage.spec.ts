import { test, expect } from '@playwright/test';
import { en, openTree, sttvEnglish, sttvOffset, technology } from './helpers';

test('card actions share contents and preserve the tree on navigation', async ({ page, context }) => {
  const tech = technology('tech_ordered_retreat');
  const queries: unknown[] = [];
  await context.route('**/api/trees/technology-tooltip', route => {
    const body = route.request().postDataJSON(); queries.push(body);
    const section = [{ kind: 'condition', text: 'Rare outcome' }];
    return route.fulfill({ json: { ...body, name: 'Ordered Retreat', description: '§YDetails§!',
      sections: { research_options: section, researched_grants: section, research_progress: section } } });
  });
  await page.goto('/'); await sttvEnglish(page);
  await openTree(page, [tech, ...Array.from({ length: 30 }, (_, i) => technology('other_' + i))], {}, false);
  const card = page.locator('[data-technology-id="tech_ordered_retreat"]');
  await card.scrollIntoViewIfNeeded(); await card.focus(); await card.hover();
  expect(queries).toHaveLength(0);
  await card.click();
  const tip = page.getByRole('tooltip');
  await expect(tip.getByRole('heading', { level: 3 })).toHaveText([en.sttv_tooltip_options, en.sttv_tooltip_grants, en.sttv_tooltip_progress]);
  const contents = await tip.innerText();
  await page.keyboard.press('Escape'); await expect(card).toBeFocused();
  await card.press('Shift+F10'); await expect(page.getByRole('menuitem')).toBeFocused();
  await page.keyboard.press('Escape'); await expect(card).toBeFocused();
  const before = await sttvOffset(page);
  await card.click({ button: 'right' });
  await page.getByRole('menuitem').click();
  await expect(page).toHaveURL(/#\/technology\/tech_ordered_retreat\?lang=en&dlc=$/);
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Ordered Retreat');
  expect(await page.locator('article .sttv-tooltip-details').innerText()).toBe(contents);
  await page.goBack();
  await expect(card).toBeVisible();
  expect(await sttvOffset(page)).toEqual(before);
  const newTab = context.waitForEvent('page');
  await card.click({ button: 'middle' });
  const other = await newTab;
  await expect(other.getByRole('heading', { level: 1 })).toHaveText('Ordered Retreat');
  await other.reload(); await expect(other.getByRole('heading', { level: 1 })).toHaveText('Ordered Retreat');
  expect(queries.every(q => JSON.stringify(q) === JSON.stringify({ technology_id: tech.id, language: 'en', enabled_dlc: [] }))).toBe(true);
  await expect(card).toBeVisible(); expect(await sttvOffset(page)).toEqual(before);
});

test('direct links use defaults and report an unknown technology without building a tree', async ({ page }) => {
  const calls: string[] = [];
  await page.route('**/api/**', route => {
    calls.push(new URL(route.request().url()).pathname);
    expect(route.request().postDataJSON()).toEqual({ technology_id: 'unknown', language: 'ru' });
    return route.fulfill({ status: 404, json: { error: 'technology_not_found' } });
  });
  await page.goto('/#/technology/unknown');
  await expect(page.locator('article')).toContainText('Технология unknown не найдена');
  await expect(page.locator('article a')).toHaveAttribute('href', '#/tree');
  expect(calls).toEqual(['/api/trees/technology-tooltip']);
});

test('published Living Metal page and card show both outcomes of the same anomaly', async ({ page }) => {
  test.skip(!process.env.STTV_TEST_URL, 'Requires the published game dataset');
  test.setTimeout(180000);
  await page.goto('/'); await sttvEnglish(page);
  await page.getByRole('button', { name: en.sttv_nav_tree, exact: true }).click();
  const card = page.locator('[data-technology-id="tech_mine_living_metal"]');
  await card.click({ timeout: 90000 });
  const tip = page.getByRole('tooltip');
  await expect(tip.getByRole('heading', { name: en.sttv_tooltip_progress })).toBeVisible({ timeout: 120000 });
  const content = await tip.innerText();
  expect(content).toContain('+25%');
  await page.keyboard.press('Escape');
  await card.click({ button: 'right' });
  await page.getByRole('menuitem').click();
  const article = page.locator('article .sttv-tooltip-details');
  await expect(article.getByRole('heading', { name: en.sttv_tooltip_grants })).toBeAttached();
  expect(await article.innerText()).toBe(content);
  await page.reload();
  await expect(article.getByRole('heading', { name: en.sttv_tooltip_options })).toBeAttached();
  expect(await article.innerText()).toBe(content);
});

import { test, expect, type Page } from '@playwright/test';
import { en, ru, mockTexts, png, sttvEnglish, technology, treeFixture } from './helpers';

const dlcs = [
  { id: 'dlc040', name: { ru: 'Кочевники', en: 'Nomads' }, thumbnail: 'dlc/nomads/thumbnail.png' },
  { id: 'dlc001', name: { ru: 'Символы господства', en: 'Symbols of Domination' }, thumbnail: null },
  { id: 'dlc032', name: { ru: 'Машинный век', en: 'The Machine Age' }, thumbnail: 'dlc/missing.png' },
];
async function setup(page: Page) {
  const calls = { catalogs: 0, selections: [] as (string[] | undefined)[], deletes: 0, failOpen: false, failClear: false };
  const techs = [technology('a'), technology('b', 1)];
  await mockTexts(page, techs);
  await page.route('**/api/trees/reference/dlcs', route => {
    calls.catalogs++;
    return route.fulfill({ json: { items: dlcs } });
  });
  await page.route('**/game-assets/dlc/**', route => route.request().url().endsWith('missing.png')
    ? route.fulfill({ status: 404 }) : route.fulfill({ contentType: 'image/png', body: png }));
  await page.route('**/api/trees/reference', async route => {
    if (route.request().method() === 'DELETE') {
      calls.deletes++;
      return route.fulfill(calls.failClear ? { status: 409, json: { reason: 'cleanup busy' } } : { json: { removed_collections: 3 } });
    }
    const selected = route.request().postDataJSON().enabled_dlc as string[] | undefined;
    calls.selections.push(selected);
    return route.fulfill(calls.failOpen ? { status: 503, json: { reason: 'server busy' } }
      : { json: treeFixture(techs, { b: 'a' }, selected ?? dlcs.map(item => item.id)) });
  });
  await page.goto('/');
  return calls;
}
test('navigation, tabs, localized DLC images, draft, empire mode and explicit builds', async ({ page }) => {
  const calls = await setup(page);
  const button = (name: string) => page.getByRole('button', { name, exact: true });
  const tab = (name: string) => page.getByRole('tab', { name, exact: true });
  const toggle = (name: string) => page.getByRole('switch', { name, exact: true });
  await expect(page.locator('input[type=file]')).toHaveCount(0);
  await button(ru.sttv_nav_game).click();
  await expect(tab('DLC')).toHaveAttribute('aria-selected', 'true');
  await expect(page.locator('[data-dlc-id]')).toHaveText([/Кочевники/, /Машинный век/, /Символы господства/]);
  await expect.poll(() => page.locator('[data-dlc-id=dlc040] img').evaluate(img => (img as HTMLImageElement).naturalWidth)).toBe(1);
  for (const id of ['dlc001', 'dlc032']) await expect(page.locator('[data-dlc-id=' + id + '] img')).toHaveCount(0);
  await toggle('Машинный век').click();
  await tab('DLC').press('ArrowRight');
  await expect(tab(ru.sttv_tab_empire)).toBeFocused();
  const group = page.locator('.sttv-empire-inputs');
  await group.evaluate(el => el.appendChild(document.createElement('input')));
  await expect(group.locator('input')).toBeDisabled();
  await toggle(ru.sttv_reference_mode).click();
  await expect(group.locator('input')).toBeEnabled();
  await button(ru.sttv_nav_tree).click();
  await expect(page.getByText(ru.sttv_empire_placeholder).first()).toBeVisible();
  await button(ru.sttv_nav_game).click();
  await expect(tab(ru.sttv_tab_empire)).toHaveAttribute('aria-selected', 'true');
  await tab(ru.sttv_tab_empire).press('Home');
  await expect(toggle('Машинный век')).not.toBeChecked();
  await sttvEnglish(page);
  await expect(page.locator('[data-dlc-id]')).toHaveText([/Nomads/, /Symbols of Domination/, /The Machine Age/]);
  await expect(toggle('The Machine Age')).not.toBeChecked();
  await button(en.sttv_dlc_apply).click();
  expect(calls.selections).toEqual([]);
  await tab(en.sttv_tab_empire).click(); await toggle(en.sttv_reference_mode).click();
  await button(en.sttv_nav_tree).click();
  await expect(page.locator('[data-technology-id]')).toHaveCount(2);
  expect(calls.selections).toEqual([['dlc040', 'dlc001']]);
  await button(en.sttv_nav_system).click(); await button(en.sttv_nav_tree).click();
  expect(calls.catalogs).toBe(1); expect(calls.selections).toHaveLength(1);
});
test('empty and partial DLC selections, retry, discard and clearing preserve the applied selection', async ({ page }) => {
  const calls = await setup(page);
  const button = (name: string) => page.getByRole('button', { name, exact: true });
  await button(ru.sttv_nav_tree).click();
  await expect(page.locator('[data-technology-id]')).toHaveCount(2);
  await button(ru.sttv_nav_game).click();
  const switches = page.getByRole('switch');
  await expect(switches).toHaveCount(3);
  for (const element of await switches.all()) await element.click();
  calls.failOpen = true;
  await button(ru.sttv_dlc_apply).click();
  await expect(page.getByRole('status')).toContainText('server busy');
  await button(ru.sttv_nav_tree).click();
  await expect(page.locator('[data-technology-id=a]')).toBeVisible();
  await button(ru.sttv_nav_game).click();
  await button(ru.sttv_dlc_discard).click();
  await expect(switches.first()).toBeChecked();
  for (const element of await switches.all()) await element.click();
  calls.failOpen = false;
  await button(ru.sttv_dlc_apply).click(); await expect(button(ru.sttv_dlc_apply)).toBeDisabled();
  expect(calls.selections.at(-1)).toEqual([]);
  await switches.first().click(); await button(ru.sttv_dlc_apply).click();
  await expect(button(ru.sttv_dlc_apply)).toBeDisabled();
  expect(calls.selections.at(-1)).toEqual(['dlc040']);
  await button(ru.sttv_nav_system).click();
  calls.failClear = true; await button(ru.sttv_ref_clear).click();
  await expect(page.getByRole('status')).toContainText('cleanup busy');
  const opens = calls.selections.length;
  await button(ru.sttv_nav_tree).click(); await expect(page.locator('[data-technology-id=b]')).toBeVisible();
  expect(calls.selections).toHaveLength(opens);
  await button(ru.sttv_nav_system).click(); calls.failClear = false;
  await button(ru.sttv_ref_clear).evaluate(el => {
    const clear = el as HTMLButtonElement;
    clear.click(); clear.click();
  });
  await expect(page.getByRole('status')).toContainText('3');
  expect(calls.deletes).toBe(2);
  await button(ru.sttv_nav_tree).click();
  await expect(page.locator('[data-technology-id=b]')).toBeVisible();
  expect(calls.selections.slice(opens)).toEqual([['dlc040']]);
});

test('a delayed reference response cannot replace the empire view', async ({ page }) => {
  const calls = await setup(page);
  let resume!: () => void;
  const pending = new Promise<void>(resolve => { resume = resolve; });
  await page.route('**/api/trees/reference', async route => { await pending; await route.fallback(); });
  await page.getByRole('button', { name: ru.sttv_nav_tree, exact: true }).click();
  await page.getByRole('button', { name: ru.sttv_nav_game, exact: true }).click();
  await page.getByRole('tab', { name: ru.sttv_tab_empire }).click();
  await page.getByRole('switch', { name: ru.sttv_reference_mode }).click();
  await page.getByRole('button', { name: ru.sttv_nav_tree, exact: true }).click();
  const localized = Promise.all(['en', 'ru'].map(language => page.waitForResponse(response =>
    response.url().endsWith('/api/localization/lookup') && response.request().postDataJSON().language === language)));
  resume(); await localized;
  await expect.poll(() => calls.selections.length).toBe(1);
  await expect(page.getByText(ru.sttv_empire_placeholder, { exact: true })).toBeVisible();
  await expect(page.locator('[data-technology-id]')).toHaveCount(0);
});

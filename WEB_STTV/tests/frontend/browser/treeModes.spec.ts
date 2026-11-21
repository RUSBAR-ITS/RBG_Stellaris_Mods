import { expect, test } from '@playwright/test';
import { en, ru, mockTexts, technology, treeFixture, sttvEnglish } from './helpers';

test('tree settings preserve an ordinary child of a hidden cross-area parent', async ({ page }) => {
  const techs = [technology('event', 2, 'society'), technology('child', 1)];
  techs[0].name = 'Longest title in this tree '.repeat(14);
  await mockTexts(page, techs);
  await page.route('**/api/trees/reference', route => {
    const { mixed_trees, hide_event_technologies } = route.request().postDataJSON();
    const result = treeFixture(techs, { child: 'event' });
    for (const n of result.items) {
      n.layout_area = mixed_trees ? 'society' : n.area;
      n.event_only = n._id === 'event';
    }
    const hidden = result.items.filter(n => n.event_only && hide_event_technologies);
    return route.fulfill({ json: { ...result, mixed_trees, hide_event_technologies,
      tree_id: JSON.stringify([mixed_trees, hide_event_technologies]), hidden_layout: hidden,
      items: result.items.filter(n => !hidden.includes(n)) } });
  });
  await page.goto('/');
  const button = (name: string) => page.getByRole('button', { name, exact: true });
  await button(ru.sttv_nav_tree).click();
  const event = page.locator('[data-technology-id=event]');
  const child = page.locator('[data-technology-id=child]');
  const branch = page.locator('[data-connection-child=child]');
  await expect(event.locator('.sttv-card-content')).toHaveCSS('background-image', /repeating-linear-gradient/);
  await expect(branch).toHaveCount(0);
  await button(ru.sttv_nav_system).click();
  await page.getByRole('tab', { name: ru.sttv_tab_tree_settings }).click();
  await page.getByRole('switch', { name: ru.sttv_mixed_trees }).click();
  await expect(page.getByRole('switch', { name: ru.sttv_mixed_trees })).toBeChecked();
  await sttvEnglish(page);
  await button(en.sttv_nav_tree).click();
  await expect(branch).toHaveCount(1);
  await expect(page.locator('section[data-area=society] [data-technology-id=child]')).toHaveAttribute('data-area', 'physics');
  const position = () => child.evaluate(el => el.parentElement!.getAttribute('style'));
  const before = await position();
  await button(en.sttv_day_theme).click();
  await expect(event.locator('.sttv-card-content')).toHaveCSS('background-image', /repeating-linear-gradient/);
  await button(en.sttv_nav_system).click();
  const hide = page.getByRole('switch', { name: en.sttv_hide_event_technologies });
  await hide.click(); await expect(hide).toBeChecked();
  await button(en.sttv_nav_tree).click();
  await expect(event).toHaveCount(0);
  await expect(branch).toHaveCount(0);
  await expect(child).toHaveCount(1);
  expect(await position()).toEqual(before);
  await button(en.sttv_nav_system).click(); await hide.click(); await expect(hide).not.toBeChecked();
  await button(en.sttv_nav_tree).click();
  await expect(branch).toHaveCount(1);
  expect(await position()).toEqual(before);
});

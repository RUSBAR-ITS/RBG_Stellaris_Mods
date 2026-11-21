import { test, expect } from '@playwright/test';
import { ru } from './helpers';

test('real bridge remains above the vertical route with independent hover colors in both themes', async ({ page }) => {
  test.skip(!process.env.STTV_TEST_URL, 'Requires the published server');
  await page.goto('/');
  await page.getByRole('button', { name: ru.sttv_nav_tree, exact: true }).click();
  await expect(page.locator('[data-connection-bridge]').first()).toBeAttached({ timeout: 90000 });
  const bridge = page.locator('[data-connection-bridge]').first();
  const path = bridge.locator('.sttv-bridge-stroke'), underlay = bridge.locator('.sttv-bridge-underlay');
  const original = await path.getAttribute('d');
  const order = () => bridge.evaluate(e => Array.from(e.parentElement!.children).map(n => n.getAttribute('data-connection-segment') ?? n.getAttribute('data-connection-bridge')));
  const before = await order();
  for (const theme of ['night', 'day']) {
    if (theme === 'day') await page.getByRole('button', { name: ru.sttv_day_theme, exact: true }).click();
    const parent = page.locator('[data-technology-id="tech_energy_torpedoes_1"]');
    await parent.scrollIntoViewIfNeeded(); await parent.hover();
    await page.locator('#sttv-viewport-content').evaluate(e => { e.scrollLeft = 650; });
    await parent.hover();
    await expect(bridge).toHaveAttribute('data-role', 'children');
    await expect(path).toHaveCSS('stroke', theme === 'night' ? 'rgb(242, 179, 102)' : 'rgb(155, 79, 11)');
    await page.locator('[data-technology-id="tech_energy_torpedoes_2"]').hover();
    await expect(bridge).toHaveAttribute('data-role', 'parent');
    await expect(path).toHaveCSS('stroke', theme === 'night' ? 'rgb(115, 191, 255)' : 'rgb(23, 104, 166)');
    await page.locator('[data-technology-id="tech_lasers_4"]').hover();
    await expect(bridge).toHaveAttribute('data-role', 'default');
    const vertical = page.locator('[data-connection-segment][data-parent="tech_lasers_4"]').first();
    await expect(vertical).toHaveAttribute('data-role', 'children');
    expect(await path.getAttribute('d')).toBe(original);
    expect(await order()).toEqual(before);
    expect(await underlay.evaluate(e => getComputedStyle(e).stroke)).toBe(await page.locator('.sttv-viewport').evaluate(e => getComputedStyle(e).backgroundColor));
  }
  expect(before.indexOf('sttv-crossing-0')).toBeGreaterThan(before.indexOf('sttv-segment-15'));
  await expect(page.locator('.sttv-connections').first()).toHaveCSS('pointer-events', 'none');
});

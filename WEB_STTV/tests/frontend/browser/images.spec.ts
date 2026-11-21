import { test, expect } from '@playwright/test';
import { en, ru, sttvEnglish } from './helpers';

test('published catalog, images, translations and tree are available on the server', async ({ page }) => {
  test.skip(!process.env.STTV_TEST_URL, 'Requires the published Stellaris test server');
  test.setTimeout(180000);
  await page.goto('/');
  await page.getByRole('button', { name: ru.sttv_nav_game, exact: true }).click();
  await expect(page.locator('[data-dlc-id]')).toHaveCount(36);
  const images = page.locator('[data-dlc-id] img');
  await expect.poll(() => images.evaluateAll(items => items.filter(img => (img as HTMLImageElement).naturalWidth > 0).length)).toBe(32);
  await expect(page.getByRole('switch', { name: 'Немезис' })).toBeChecked();
  await expect(page.getByRole('switch', { name: 'Машинный век' })).toBeChecked();
  await sttvEnglish(page);
  await expect(page.getByRole('switch', { name: 'The Machine Age' })).toBeChecked();
  await page.getByRole('button', { name: en.sttv_nav_tree, exact: true }).click();
  const card = page.locator('[data-technology-id=tech_lasers_3]');
  await expect(card).toBeVisible({ timeout: 120000 });
  await expect.poll(() => card.locator('.sttv-card-image img').evaluate(img => (img as HTMLImageElement).naturalWidth)).toBeGreaterThan(0);
  await expect(page.locator('[data-connection-child]').first()).toBeAttached();
});

import { test, expect } from '@playwright/test';
import { sttvEnglish, openTree, technology as makeTechnology, sttvOffset, en } from './helpers';

test('card details load on demand and keep condition groups, source blocks and formulas', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  const tech = makeTechnology('tech_conditions');
  const calls: unknown[] = [];
  await page.route('**/api/trees/technology-tooltip', route => {
    const input = route.request().postDataJSON();
    calls.push(input);
    if (calls.length === 1) return route.fulfill({ status: 503, json: {} });
    return route.fulfill({ json: { ...input, sections: {
      prerequisites: [{ kind: 'group', text: 'One must be true', children: [
        { kind: 'technology', text: '§YTech A§!' }, { kind: 'technology', text: 'Tech B' }] }],
      potential: [{ kind: 'condition', text: 'DLC enabled' }],
      allow: [{ kind: 'unrecognized', expression: { key: '<unknown>' } }],
      weight_modifier: [{ kind: 'modifier', operations: [
        { kind: 'operation', text: '×Formula', formula: [{ kind: 'operation', text: 'Base 10' }] }],
        condition: { kind: 'group', text: 'All of the following are true:', children: [
          { kind: 'condition', text: 'After 50 years' }, { kind: 'group', text: 'At least one is true:', children: [
            { kind: 'condition', text: 'Has §YTech A§!' }, { kind: 'condition', text: 'Has Tech B' }] }] } },
        { kind: 'modifier', operations: [{ kind: 'operation', text: '+5' }], condition: { kind: 'condition', text: 'Flag set' } }],
    } } });
  });
  await openTree(page, [tech]);
  const card = page.locator('[data-technology-id="tech_conditions"]');
  await expect(card).toBeVisible();
  expect(calls).toHaveLength(0);
  await card.hover();
  const tip = page.getByRole('tooltip');
  await expect(tip).toContainText(en.sttv_tooltip_error);
  await expect(tip).toContainText(tech.description);
  await page.mouse.move(10, 10);
  await expect(tip).toHaveCount(0);
  await card.focus();
  await expect(tip.getByRole('heading', { level: 3 })).toHaveText([
    en.sttv_tooltip_prerequisites, en.sttv_tooltip_availability, en.sttv_tooltip_weight]);
  await expect(tip.locator('section').nth(0).locator('li li')).toHaveText(['Tech A', 'Tech B']);
  await expect(tip.locator('[data-game-color="Y"]').first()).toHaveCSS('color', 'rgb(247, 252, 52)');
  await expect(tip.locator('h4')).toHaveText([en.sttv_tooltip_potential, en.sttv_tooltip_allow]);
  await expect(tip.locator('code')).toHaveText('{"key":"<unknown>"}');
  const rules = tip.locator('section').last().locator(':scope > ul > li');
  await expect(rules).toHaveCount(2);
  await expect(rules.first()).toContainText('(×Formula) All of the following are true:');
  await expect(rules.first().locator(':scope > ul > li').last()).toContainText('At least one is true:');
  await expect(rules.first()).toContainText('Base 10');
  await expect(rules.last()).toHaveText('(+5) Flag set');
  await page.keyboard.press('Tab');
  await card.focus();
  await expect(tip).toContainText('After 50 years');
  expect(calls).toEqual(Array(2).fill({ language: 'en', technology_id: tech.id }));
});

test('inline game icons preserve whitespace, literal markers and nested colors', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  const tech = makeTechnology('tech_inline_icons');
  tech.name = '£energy£ and £minerals£';
  tech.description = '§HBefore £blocker£ §Y+1§! after§!  £unknown£ £unclosed';
  await openTree(page, [tech]);
  const card = page.locator('[data-technology-id="tech_inline_icons"]');
  const title = card.locator('.sttv-card-title');
  await expect(title.getByRole('img')).toHaveCount(2);
  await expect(title.getByRole('img', { name: en.sttv_icon_energy })).toHaveAttribute('src', /\/resources\/energy\.png$/);
  await expect(title).toHaveText(' and ');
  await card.focus();
  const tip = page.getByRole('tooltip');
  await expect(tip.getByRole('img', { name: en.sttv_icon_blocker })).toHaveAttribute('src', /\/text_icons\/text_icon_tile_blocker\.png$/);
  await expect(tip.locator('[data-game-color="Y"]')).toHaveText('+1');
  await expect(tip.locator('[data-game-color="H"]')).toHaveText(['Before ', ' ', ' after']);
  expect(await tip.textContent()).toContain('Before  +1 after  £unknown£ £unclosed');
});

test('oversized literal descriptions remain reachable without scrolling the field', async ({ page }) => {
  await page.setViewportSize({ width: 900, height: 500 });
  await page.goto('/'); await sttvEnglish(page);
  const technology = makeTechnology('tech_long');
  const markup = '§GRaw $key$ [Scope.Name] <b>§Yliteral§!</b>§! plain ';
  const description = markup.repeat(160);
  technology.description = description;
  await openTree(page, [technology]);
  const card = page.locator('[data-technology-id="tech_long"]');
  await card.hover();
  const tooltip = page.getByRole('tooltip');
  await expect(tooltip).toContainText('Raw $key$ [Scope.Name] <b>literal</b> plain '.repeat(160));
  await expect(tooltip.locator('[data-game-color="G"]').nth(1)).toHaveText('</b>');
  await expect(tooltip.locator('[data-game-color="Y"]').first()).toHaveText('literal');
  await expect(tooltip.locator('[data-game-color]').filter({ hasText: 'plain' })).toHaveCount(0);
  await expect(tooltip.locator('b')).toHaveCount(0);
  const rect = (await tooltip.boundingBox())!;
  expect(rect.x).toBeGreaterThanOrEqual(8); expect(rect.y).toBeGreaterThanOrEqual(8);
  expect(rect.x + rect.width).toBeLessThanOrEqual(892);
  expect(rect.y + rect.height).toBeLessThanOrEqual(492);
  const before = await sttvOffset(page);
  await page.mouse.wheel(0, 300);
  await expect.poll(() => tooltip.evaluate(element => element.scrollTop)).toBeGreaterThan(0);
  expect(await sttvOffset(page)).toEqual(before);
  await page.mouse.move(10, 10); await expect(tooltip).toHaveCount(0);
});
test('language selection changes only after confirmation; cards remain read-only and focusable', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  const technology = makeTechnology('tech_base');
  await openTree(page, [technology]);
  const card = page.locator('[data-technology-id="tech_base"]');
  const trigger = page.getByRole('button', { name: en.sttv_language, exact: true });
  await trigger.focus(); await page.keyboard.press('ArrowDown');
  await page.keyboard.press('Home');
  await expect(card).toContainText('tech_base');
  await expect(page.getByRole('option').last()).toHaveAttribute('aria-selected', 'true');
  await page.keyboard.press('Escape');
  await expect(page.locator('html')).toHaveAttribute('lang', 'en');
  await expect(trigger).toBeFocused();
  await card.focus(); await expect(page.getByRole('tooltip')).toContainText('tech_base details');
  await expect(card.locator('button')).toHaveCount(0);
  await page.getByRole('button', { name: en.sttv_day_theme, exact: true }).focus();
  await expect(page.getByRole('tooltip', { name: en.sttv_day_theme, exact: true })).toBeVisible();
});

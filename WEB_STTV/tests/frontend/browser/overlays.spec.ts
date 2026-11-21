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
    return route.fulfill({ json: { ...input, name: tech.name, description: tech.description, sections: {
      prerequisites: [{ kind: 'group', text: 'One must be true', children: [
        { kind: 'technology', text: '§YTech A§!' }, { kind: 'technology', text: 'Tech B' }] }],
      potential: [{ kind: 'condition', text: 'DLC enabled' }],
      allow: [{ kind: 'partial', text: 'Part of this condition needs interpretation', expression: { key: '<unknown>' } }],
      weight_modifier: [{ kind: 'modifier', operations: [
        { kind: 'operation', text: '×Formula', formula: [{ kind: 'operation', text: 'Base 10' }] }],
        condition: { kind: 'group', text: 'All of the following are true:', children: [
          { kind: 'condition', text: 'After 50 years' }, { kind: 'group', text: 'At least one is true:', children: [
            { kind: 'condition', text: 'Has §YTech A§!' }, { kind: 'condition', text: 'Has Tech B' }] }] } },
        { kind: 'modifier', operations: [{ kind: 'operation', text: '+5' }], condition: { kind: 'condition', text: 'Flag set' } }],
    } } });
  });
  await openTree(page, [tech], {}, false);
  const card = page.locator('[data-technology-id="tech_conditions"]');
  await expect(card).toBeVisible();
  expect(calls).toHaveLength(0);
  await card.hover(); await card.focus();
  expect(calls).toHaveLength(0);
  await card.press('Space');
  const tip = page.getByRole('tooltip');
  await expect(tip).toContainText(en.sttv_technology_request_error);
  await expect(card).toBeFocused();
  await page.mouse.move(10, 10); await expect(tip).toBeVisible();
  await page.keyboard.press('Escape'); await expect(card).toBeFocused();
  await expect(tip).toHaveCount(0);
  await card.press('Enter');
  await expect(tip.getByRole('heading', { level: 3 })).toHaveText([
    en.sttv_tooltip_prerequisites, en.sttv_tooltip_availability, en.sttv_tooltip_weight]);
  await expect(tip.locator('section').nth(0).locator('li li')).toHaveText(['Tech A', 'Tech B']);
  await expect(tip.locator('[data-game-color="Y"]').first()).toHaveCSS('color', 'rgb(247, 252, 52)');
  await expect(tip.locator('h4')).toHaveText([en.sttv_tooltip_potential, en.sttv_tooltip_allow]);
  await expect(tip.locator('code')).not.toBeVisible();
  await tip.getByText(en.sttv_condition_details).click();
  await expect(tip.locator('code')).toBeVisible();
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
  expect(calls).toEqual(Array(2).fill({ language: 'en', technology_id: tech.id, enabled_dlc: [] }));
});

test('resetting research progress keeps the open tree and fetches a fresh tooltip on click', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  const tech = makeTechnology('tech_progress');
  let lookups = 0;
  await page.route('**/api/trees/technology-tooltip', route => route.fulfill({ json: {
    ...route.request().postDataJSON(), name: tech.name, description: tech.description, sections: { research_progress: [
      { kind: 'progress', text: 'Project ' + ++lookups, children: [{ kind: 'progress', text: '+25%' }] }] } } }));
  await page.route('**/api/trees/research-progress', route => route.fulfill({ json: { removed_collections: 0 } }));
  await openTree(page, [tech], {}, false);
  const card = page.locator('[data-technology-id="tech_progress"]');
  await card.click();
  await expect(page.getByRole('tooltip')).toContainText('Project 1');
  const position = await sttvOffset(page);
  await page.getByRole('button', { name: en.sttv_nav_system, exact: true }).click();
  await page.getByRole('button', { name: en.sttv_reset_progress, exact: true }).click();
  await expect(page.getByText(en.sttv_reset_done_progress)).toBeVisible();
  expect(lookups).toBe(1);
  await page.getByRole('button', { name: en.sttv_nav_tree, exact: true }).click();
  expect(await sttvOffset(page)).toEqual(position);
  await card.click();
  await expect(page.getByRole('tooltip')).toContainText('Project 2');
});

test('a reset in another tab discards a delayed tooltip response', async ({ page, context }) => {
  let release!: () => void;
  const delayed = new Promise<void>(resolve => { release = resolve; });
  let calls = 0;
  await page.route('**/api/trees/technology-tooltip', async route => {
    calls++;
    if (calls === 1) await delayed;
    await route.fulfill({ json: { ...route.request().postDataJSON(),
      name: calls === 1 ? 'Old result' : 'Fresh result', description: '', sections: {} } });
  });
  const lookup = page.waitForRequest('**/api/trees/technology-tooltip');
  await page.goto('/#/technology/test?lang=en');
  await lookup;
  const settings = await context.newPage();
  await settings.route('**/api/trees/technology-tooltips', route => route.fulfill({ json: { removed_collections: 1 } }));
  await settings.goto('/'); await sttvEnglish(settings);
  const broadcast = page.evaluate(() => new Promise<void>(resolve => {
    const channel = new BroadcastChannel('sttv-tooltip-reset');
    channel.onmessage = () => { channel.close(); resolve(); };
  }));
  await settings.getByRole('button', { name: en.sttv_nav_system, exact: true }).click();
  await settings.getByRole('button', { name: en.sttv_reset_tooltips, exact: true }).click();
  await broadcast;
  release();
  await expect(page.locator('article')).toContainText(en.sttv_reset_done_tooltips);
  expect(calls).toBe(1);
  await page.goto('/#/tree');
  await page.goto('/#/technology/test?lang=en');
  await expect(page.locator('article h1')).toHaveText('Fresh result');
  expect(calls).toBe(2);
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
  await card.press('Enter');
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
  await card.click();
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
  await page.keyboard.press('Escape'); await expect(tooltip).toHaveCount(0);
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
  await card.press('Enter'); await expect(page.getByRole('tooltip')).toContainText('tech_base details');
  await page.keyboard.press('Escape');
  await expect(card.locator('button')).toHaveCount(0);
  await page.getByRole('button', { name: en.sttv_day_theme, exact: true }).focus();
  await expect(page.getByRole('tooltip', { name: en.sttv_day_theme, exact: true })).toBeVisible();
});

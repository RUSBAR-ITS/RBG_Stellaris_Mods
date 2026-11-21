import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { chromium, expect } from '@playwright/test';

const url = process.argv[2];
if (!url) throw new Error('Supply the URL of the deployed reference frontend.');
const browser = await chromium.launch({ executablePath: process.env.STTV_BROWSER_EXECUTABLE });
try {
  for (const lang of ['ru', 'en']) {
    const labels = JSON.parse(readFileSync(new URL('../../src/frontend/locales/' + lang + '.json', import.meta.url)));
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(url);
    const button = name => page.getByRole('button', { name, exact: true });
    if (lang === 'en') {
      await page.locator('.sttv-language-selector button').click();
      await page.getByRole('option', { name: 'English' }).click();
      await button(labels.sttv_day_theme).click();
    }
    for (const all of [true, false]) {
      if (!all) {
        await button(labels.sttv_nav_game).click();
        const selected = page.locator('[data-dlc-id] [role=switch][aria-checked=true]');
        await expect(selected.first()).toBeVisible();
        while (await selected.count()) await selected.first().click();
        await button(labels.sttv_dlc_apply).click();
        await expect(button(labels.sttv_dlc_apply)).toBeDisabled();
      }
      for (const mixed of [false, true]) {
        let baseline;
        for (const hide of [false, true]) {
          await button(labels.sttv_nav_system).click();
          await page.getByRole('tab', { name: labels.sttv_tab_tree_settings }).click();
          for (const [key, value] of [['mixed_trees', mixed], ['hide_event_technologies', hide]]) {
            const toggle = page.getByRole('switch', { name: labels['sttv_' + key] });
            await expect(toggle).toBeEnabled({ timeout: 120000 });
            if ((await toggle.getAttribute('aria-checked')) !== String(value)) {
              await toggle.click();
              await expect(toggle).toHaveAttribute('aria-checked', String(value), { timeout: 120000 });
            }
          }
          await button(labels.sttv_nav_tree).click();
          const cards = page.locator('[data-technology-id]');
          await expect(cards.first()).toBeAttached({ timeout: 120000 });
          await expect(page.locator('.sttv-scaled-field')).toHaveAttribute('data-scale', '0.5');
          const current = await cards.evaluateAll(elements => Object.fromEntries(elements.map(el => {
            const cell = el.parentElement, section = el.closest('.sttv-research-area');
            const pos = [section.dataset.area, section.offsetTop, cell.offsetLeft, cell.offsetTop, cell.offsetHeight];
            const striped = getComputedStyle(el.querySelector('.sttv-card-content')).backgroundImage.includes('repeating-linear-gradient');
            return [el.dataset.technologyId, { pos, striped, area: el.dataset.area }];
          })));
          if (hide) {
            assert.deepEqual(current, Object.fromEntries(Object.entries(baseline).filter(([, n]) => !n.striped)));
          } else {
            baseline = current;
            assert(current.tech_mining_drone_weapon_1.striped);
            if (all) assert(current.tech_trinary_computing.striped && !current.tech_colossus.striped);
          }
          const edges = await page.locator('[data-connection-child]').evaluateAll(elements =>
            Object.fromEntries(elements.map(el => [el.dataset.connectionChild, el.dataset.connectionParent])));
          for (const [child, parent] of Object.entries(edges)) assert(current[child] && current[parent]);
          if (all) for (const child of ['tech_encryption_1', 'tech_decryption_1']) {
            assert.equal(current[child].area, 'physics');
            assert.equal(current[child].pos[0], mixed ? 'society' : 'physics');
            assert.equal(edges[child], mixed ? 'tech_colonial_bureaucracy' : undefined);
          }
          console.log(lang, all ? 'all DLC' : 'no DLC', { mixed, hide, cards: Object.keys(current).length, edges: Object.keys(edges).length });
        }
      }
    }
    await page.goto(new URL('#/technology/tech_mining_drone_weapon_1?lang=' + lang, url).href);
    await expect(page.locator('.sttv-technology-page h1')).toBeVisible({ timeout: 60000 });
    assert.deepEqual(errors, []);
    await page.close();
  }
} finally {
  await browser.close();
}

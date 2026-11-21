import { expect, type Page } from '@playwright/test';
import { sttvPlaceTrees } from '../placementFixture';
import ru from '../../../src/frontend/locales/ru.json' with { type: 'json' };
import en from '../../../src/frontend/locales/en.json' with { type: 'json' };

export { ru, en };
export const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jk0kAAAAASUVORK5CYII=', 'base64');
export function technology(id: string, tier = 0, area = 'physics') {
  return { id, tier, area, name: id, description: id + ' details', cost: null as number | null, weight: null as number | null,
    levels: null as number | null, rare: false, dangerous: false, starting: false };
}
type Technology = ReturnType<typeof technology>;
export function treeFixture(techs: Technology[], parents: Record<string, string> = {}, enabled: string[] = []) {
  const nodes = new Map(techs.map(t => [t.id, { column: t.tier, children: [] as string[] }]));
  for (const [child, parent] of Object.entries(parents)) nodes.get(parent)!.children.push(child);
  const roots = techs.filter(t => !parents[t.id]).map(t => t.id);
  const { cards } = sttvPlaceTrees(roots, nodes, () => (a, b) => a.localeCompare(b));
  return { tree_id: 'test-' + enabled.join('-'), enabled_dlc: enabled, items: cards.map(({ id, column, row }) => ({
    _id: id, area: techs.find(t => t.id === id)!.area, parent_tech: parents[id] ?? null,
    children: nodes.get(id)!.children, location: { ru: [column, row], en: [column, row] } })),
    cards: Object.fromEntries(techs.map(t => [t.id, { ...t, name: t.id, description: t.id + '_desc', categories: [],
      icon: 'test_icon', source: { database: 'technologies', document_id: t.id, pointer: '' } }])) };
}
export async function mockTexts(page: Page, techs: Technology[], mockDetails = true) {
  const texts = new Map(techs.flatMap(t => [[t.id, t.name], [t.id + '_desc', t.description]] as [string, string][]));
  if (mockDetails) await page.route('**/api/trees/technology-tooltip', route => {
    const body = route.request().postDataJSON();
    const tech = techs.find(t => t.id === body.technology_id);
    return tech ? route.fulfill({ json: { ...body, name: tech.name, description: tech.description, sections: {} } })
      : route.fulfill({ status: 404, json: { error: 'technology_not_found' } });
  });
  await page.route('**/api/localization/lookup', route => {
    const { keys } = route.request().postDataJSON() as { keys: string[] };
    return route.fulfill({ json: { items: keys.map(key => ({ key, text: texts.get(key) ?? null })) } });
  });
  await page.route('**/game-assets/gfx/**', route => route.fulfill({ contentType: 'image/png', body: png }));
}
export async function openTree(page: Page, techs: Technology[], parents: Record<string, string> = {}, mockDetails = true) {
  await mockTexts(page, techs, mockDetails);
  await page.route('**/api/trees/reference', route => route.fulfill(route.request().method() === 'POST'
    ? { json: treeFixture(techs, parents) } : { status: 405 }));
  await page.getByRole('button', { name: en.sttv_nav_tree, exact: true }).click();
}
export async function sttvEnglish(page: Page) {
  await page.getByRole('button', { name: ru.sttv_language, exact: true }).click();
  await page.getByRole('option', { name: 'English', exact: true }).click();
  await expect(page.locator('html')).toHaveAttribute('lang', 'en');
}
export async function sttvReady(page: Page) {
  await openTree(page, Array.from({ length: 18 }, (_, i) => technology(i ? 'tech_' + i : 'tech_example', i % 7)));
  await expect(page.locator('[data-technology-id]')).toHaveCount(18);
}
export async function sttvOffset(page: Page) {
  return page.locator('#sttv-viewport-content').evaluate(e => ({ x: e.scrollLeft, y: e.scrollTop }));
}

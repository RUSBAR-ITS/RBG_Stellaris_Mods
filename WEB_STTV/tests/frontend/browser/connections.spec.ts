import { test, expect } from '@playwright/test';
import { sttvEnglish, openTree, technology, en } from './helpers';

test('card hover colors complete parent/child paths without rerouting or changing sibling branches', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  const nodes = Object.entries({ P: 0, A: 1, B: 2, C: 1, D: 2, E: 1 }).map(([id, tier]) => technology(id, tier));
  await openTree(page, nodes, { A: 'P', B: 'A', C: 'A', D: 'C', E: 'A' });
  await expect(page.locator('[data-connection-child]')).toHaveCount(5);
  const paths = () => page.locator('[data-connection-segment]').evaluateAll(nodes => nodes.map(n => n.getAttribute('d')));
  const before = await paths();
  const card = page.locator('[data-technology-id="C"]'); await card.hover();
  await expect(page.getByRole('tooltip')).toBeVisible();
  const colors = await page.locator('[data-connection-segment]').evaluateAll(nodes => nodes.map(node => ({
    parent: node.getAttribute('data-parent'), children: JSON.parse(node.getAttribute('data-children')!),
    role: node.getAttribute('data-role'), color: getComputedStyle(node).stroke,
  })));
  for (const line of colors) expect(line.role).toBe(line.parent === 'C' ? 'children' : line.children.includes('C') ? 'parent' : 'default');
  expect(colors.find(v => v.role === 'parent')!.color).not.toBe(colors.find(v => v.role === 'children')!.color);
  expect(colors.some(v => v.parent === 'A' && v.children.includes('C') && v.children.includes('E') && v.role === 'parent')).toBe(true);
  expect(colors.some(v => v.children.includes('E') && !v.children.includes('C') && v.role === 'default')).toBe(true);
  await page.mouse.move(5, 5);
  await expect(page.locator('.sttv-connections [data-role="parent"], .sttv-connections [data-role="children"]')).toHaveCount(0);
  expect(await paths()).toEqual(before);
  await page.getByRole('button', { name: en.sttv_day_theme, exact: true }).click();
  await card.hover();
  await expect(page.locator('.sttv-connection[data-role="parent"]').first()).toHaveCSS('stroke', 'rgb(23, 104, 166)');
  expect(await paths()).toEqual(before);
});

test('connection endpoints stay on cards through scrolling, menu changes and window resizing', async ({ page }) => {
  await page.goto('/'); await sttvEnglish(page);
  const nodes = [technology('A', 0), technology('B', 4), technology('C', 0), technology('D', 2)];
  await openTree(page, nodes, { B: 'A', C: 'B', D: 'C' });
  await expect(page.locator('[data-connection-child]')).toHaveCount(3);
  const check = async () => {
    const endpoints = await page.locator('[data-connection-child]').evaluateAll(arrows => arrows.map(arrow => {
      const child = document.querySelector(`[data-technology-id="${arrow.getAttribute('data-connection-child')}"]`)!;
      const card = child.getBoundingClientRect();
      const [x, y] = arrow.getAttribute('d')!.slice(1).split('L')[0].split(',').map(Number);
      const { x: px, y: py } = new DOMPoint(x, y).matrixTransform((arrow as SVGGraphicsElement).getScreenCTM()!);
      return Math.min(Math.hypot(px - card.left, py - (card.top + card.height / 2)),
        Math.hypot(px - card.right, py - (card.top + card.height / 2)),
        Math.hypot(px - (card.left + card.width / 2), py - card.top));
    }));
    for (const distance of endpoints) expect(distance).toBeLessThan(0.1);
  };
  await check();
  await page.locator('#sttv-viewport-content').evaluate(e => { e.scrollLeft = 300; e.scrollTop = 60; });
  await check();
  await page.getByRole('button', { name: en.sttv_collapse_menu, exact: true }).click();
  await page.setViewportSize({ width: 1000, height: 650 }); await check();
});

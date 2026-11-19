import { expect, type Page } from '@playwright/test';
import { en, ru } from './helpers';

export async function sttvZoom(page: Page, percent: number) {
  const language = await page.locator('html').getAttribute('lang');
  await page.getByRole('button', { name: language === 'ru' ? ru.sttv_zoom : en.sttv_zoom, exact: true }).click();
  await page.getByRole('option', { name: `${percent}%`, exact: true }).click();
  if (await page.locator('.sttv-scaled-field').count()) {
    await expect(page.locator('.sttv-scaled-field')).toHaveAttribute('data-scale', String(percent / 100));
  }
}

export async function sttvZoomGeometry(page: Page) {
  return page.locator('#sttv-viewport-content').evaluate(element => {
    const field = element.querySelector<HTMLElement>('.sttv-scaled-field')!;
    const card = element.querySelector<HTMLElement>('[data-technology-id]')!;
    const size = field.getBoundingClientRect();
    return { x: element.scrollLeft, y: element.scrollTop, width: element.clientWidth, height: element.clientHeight,
      scrollWidth: element.scrollWidth, scrollHeight: element.scrollHeight, fieldWidth: size.width, fieldHeight: size.height,
      scale: Number(field.dataset.scale), cardWidth: card.getBoundingClientRect().width,
      cardHeight: card.getBoundingClientRect().height, baseHeight: card.offsetHeight,
      titleHeight: card.querySelector('.sttv-card-title')!.getBoundingClientRect().height,
      titleBaseHeight: (card.querySelector('.sttv-card-title')! as HTMLElement).offsetHeight };
  });
}

export async function sttvCheckConnectionAnchors(page: Page) {
  const distances = await page.locator('[data-connection-child]').evaluateAll(arrows => arrows.map(arrow => {
    const rect = document.querySelector(`[data-technology-id="${arrow.getAttribute('data-connection-child')}"]`)!.getBoundingClientRect();
    const [x, y] = arrow.getAttribute('d')!.slice(1).split('L')[0].split(',').map(Number);
    const point = new DOMPoint(x, y).matrixTransform((arrow as SVGGraphicsElement).getScreenCTM()!);
    return Math.min(Math.hypot(point.x - rect.left, point.y - rect.top - rect.height / 2),
      Math.hypot(point.x - rect.right, point.y - rect.top - rect.height / 2),
      Math.hypot(point.x - rect.left - rect.width / 2, point.y - rect.top));
  }));
  expect(distances.length).toBeGreaterThan(0);
  for (const distance of distances) expect(distance).toBeLessThan(0.1);
}

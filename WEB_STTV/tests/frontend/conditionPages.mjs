/** Compare every published technology page with its API response and the previous acquisition records. */
import { chromium } from 'playwright';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { gzipSync, gunzipSync } from 'node:zlib';
import { join } from 'node:path';

const [base, baseline, inventoryFile, output] = process.argv.slice(2);
if (!output) throw Error('Expected URL, baseline directory, technology ID inventory and report directory');
const inventory = JSON.parse(await readFile(inventoryFile, 'utf8'));
const ids = inventory.technology_ids ?? inventory;
const langs = ['ru', 'en'];
const words = Object.fromEntries(await Promise.all(langs.map(async lang =>
  [lang, JSON.parse(await readFile(new URL('../../src/frontend/locales/' + lang + '.json', import.meta.url)))])));
const awards = ['research_options', 'researched_grants', 'research_progress'];
const sections = ['prerequisites', 'availability', 'weight', 'options', 'grants', 'progress'];
const rows = [];
const browser = await chromium.launch({ executablePath: process.env.STTV_CHROME,
  headless: true, args: ['--disable-background-timer-throttling'] });
await mkdir(output, {recursive: true});
const snapshots = join(output,'../../artifacts/after');
await mkdir(snapshots, {recursive:true});

function rewardAddresses(groups) {
  return groups.flatMap(g => g.children.filter(n => n.address && !n.address.object && !n.source && !/^(?:Source|Источник) — /u.test(n.text))
    .map(n => JSON.stringify([g.source, n.address.file, n.address.pointer, n.address.definition, n.address.calls,
      n.text?.startsWith('+') ? normalize(n.text) : null]))).sort();
}
function normalize(s) {
  return (s ?? '').replace(/§[\w!]/gu, '').replace(/£\w+£/gu,'').replace(/\s+/gu,' ').trim();
}
function failIf(condition, message) { if (condition) throw Error(message); }
let cursor = 0;
const pairs = ids.flatMap(id => langs.map(lang => [id, lang]));
async function worker() {
  const context = await browser.newContext();
  const page = await context.newPage();
  page.setDefaultTimeout(120000);
  let delivered;
  await page.route('**/api/trees/technology-tooltip', async route => {
    const upstream = await route.fetch({timeout:120000});
    try {
      const body = await upstream.body();
      delivered = JSON.parse(body.toString('utf8'));
      await route.fulfill({response:upstream, body});
    } finally {
      await upstream.dispose();
    }
  });
  while (cursor < pairs.length) {
    const [id, lang] = pairs[cursor++];
    const row = { id, lang };
    try {
      const answer = page.waitForResponse(r => r.url().endsWith('/technology-tooltip') &&
        r.request().postDataJSON()?.technology_id === id && r.request().postDataJSON()?.language === lang);
      await page.goto(base + '/?audit=' + id + '-' + lang + '#/technology/' + encodeURIComponent(id) + '?lang=' + lang,
                      {waitUntil:'domcontentloaded'});
      const response = await answer;
      failIf(!response.ok(), 'HTTP ' + response.status());
      const data = delivered;
      delivered = undefined;
      failIf(data?.technology_id !== id || data.language !== lang, 'Unexpected delivered payload');
      await writeFile(join(snapshots,id+'.'+lang+'.json.gz'),gzipSync(JSON.stringify(data),{level:1}));
      const article = page.locator('article .sttv-tooltip-details');
      await article.locator('h1').waitFor();
      row.collapsed = await article.locator('.sttv-reward-details:not([open])').count();
      await article.locator('.sttv-reward-details').evaluateAll(items => {
        for (const item of items) item.open = true;
      });
      if(row.collapsed) await page.waitForFunction(() =>
        [...document.querySelectorAll('.sttv-reward-details')].every(el=>el.open && el.querySelector(':scope > ul')));
      const actual = await article.evaluate(el => ({
        name: el.querySelector('h1').innerText, headings:[...el.querySelectorAll('h3')].map(e=>e.innerText),
        text:el.innerText, lists: el.querySelectorAll('ul ul').length,
        images:[...el.querySelectorAll('.sttv-inline-icon img')].map(img => img.getAttribute('src')),
        placeholders:el.querySelectorAll('.sttv-inline-icon .sttv-image-placeholder').length
      }));
      const part = data.sections;
      const needed = [part.prerequisites, [part.potential, part.allow, part.starting_potential].find(a=>a?.length),
        [part.weight_modifier, part.weight_notes].find(a=>a?.length), ...awards.map(k=>part[k])]
          .flatMap((items, i)=>items?.length ? [words[lang]['sttv_tooltip_' + sections[i]]] : []);
      failIf(JSON.stringify(needed)!==JSON.stringify(actual.headings), 'Section headings differ');
      failIf(normalize(data.name)!==normalize(actual.name), 'Title differs');
      const visible = normalize(actual.text);
      const raw = actual.text.match(/\|\|\||§[\w!]|£\w+£|\$[\w.@|]+\$|\\n|\[(?:root|this|from|event_target)[.:]/iu);
      failIf(raw, 'Unrendered localization markup: ' + raw?.[0]);
      const identifier = actual.text.match(/\b(?:on_[a-z_0-9]+|[a-z][a-z_]+\.\d+|event_target:[a-z_0-9]+)\b/u);
      failIf(identifier, 'Raw script identifier: ' + identifier?.[0]);
      const nodes = [];
      function collect(n) {
        if (Array.isArray(n)) { n.forEach(collect); return; }
        if (!n || typeof n !== 'object') return;
        if(n.kind==='custom_tooltip' && n.children?.some(c=>c.key==='success_text') && n.children?.some(c=>c.key==='fail_text'))
          throw Error('Mutually exclusive captions shown together');
        if(n.text) nodes.push(normalize(n.text).replace(/:+$/u,''));
        for(const k of ['children','operations','formula','condition']) collect(n[k]);
      }
      Object.values(part).forEach(collect);
      for (const txt of new Set(nodes)) failIf(txt && !visible.includes(txt), 'Missing condition: ' + txt.slice(0,160));
      failIf(nodes.length>0 && !await article.locator('ul').count(), 'Missing list');
      const brokenIcons = await article.locator('.sttv-inline-icon img').evaluateAll(async imgs => {
        await Promise.allSettled(imgs.map(img => img.decode()));
        return imgs.filter(img => !img.complete || img.naturalWidth === 0).map(img => img.src);
      });
      failIf(brokenIcons.length > 0, 'Missing icon: ' + brokenIcons.join(', '));
      failIf(await article.locator('.sttv-inline-icon .sttv-image-placeholder').count()>0,'Missing icon');
      const prior = JSON.parse(gunzipSync(await readFile(join(baseline,id+'.'+lang+'.json.gz'))));
      row.changes = {};
      for (const section of awards) {
        const old = prior.sections[section] ?? [], fresh = part[section] ?? [];
        const before = new Set(rewardAddresses(old)), after = new Set(rewardAddresses(fresh));
        const removed = [...before].filter(k => !after.has(k));
        const added = [...after].filter(k => !before.has(k));
        const sources = groups => groups.map(g => JSON.stringify(g.source));
        const oldSources = sources(old), newSources = sources(fresh);
        row.changes[section] = {removed, added, addedSources:newSources.filter(k=>!oldSources.includes(k)),
          removedSources:oldSources.filter(k=>!newSources.includes(k))};
        failIf(removed.length > 0 || row.changes[section].removedSources.length > 0,
          'Baseline reward or source was removed; inspect the address diff for '+section);
      }
      Object.assign(row, { ok:true, sections:needed.length, nodes:nodes.length, images:actual.images.length,
        diagnostics:[...new Set(data.diagnostics.map(d=>d.reason))], awards:awards.filter(s=>part[s]?.length) });
    } catch(error) { row.ok=false; row.error=String(error); }
    rows.push(row);
    if(!row.ok) console.log(id, lang, row.error);
    if(rows.length%50===0) console.log(rows.length, '/', pairs.length, 'failed:',rows.filter(r=>!r.ok).length);
  }
  await context.close();
}
async function compareCardAndPage() {
  const context = await browser.newContext();
  try {
    const page = await context.newPage();
    page.setDefaultTimeout(120000);
    await page.goto(base);
    await page.getByRole('button', {name:/^(Technology tree|Древо технологий)$/iu}).click();
    const card = page.locator('[data-technology-id="tech_lasers_2"]');
    const href = await card.getAttribute('href');
    await card.click();
    const content = page.locator('.sttv-card-overlay .sttv-tooltip-details');
    await content.locator('h2').waitFor();
    async function keyboardDetails(panel) {
      const details = panel.locator('.sttv-reward-details').first();
      const before = await panel.innerText();
      failIf(await details.locator(':scope > ul').count(), 'Collapsed reward mounted its conditions');
      await details.locator('summary').press('Enter');
      await details.locator(':scope > ul').waitFor();
      return [before, await panel.innerText()];
    }
    const overlay = await keyboardDetails(content);
    const tab = await context.newPage();
    await tab.goto(new URL(href, page.url()).href);
    const article = tab.locator('article .sttv-tooltip-details');
    await article.locator('h1').waitFor({timeout:120000});
    const standalone = await keyboardDetails(article);
    failIf(JSON.stringify(overlay) !== JSON.stringify(standalone), 'Card and page content differ');
    await writeFile(join(output,'card-page.json'), JSON.stringify({id:'tech_lasers_2', sameContent:true,
      sameExpandedOutcome:true, keyboardOpen:true}));
  } finally {
    await context.close();
  }
}
try {
  await Promise.all(Array.from({length:4},worker));
  if(ids.includes('tech_lasers_2')) await compareCardAndPage();
}
finally {
  await browser.close();
  await writeFile(join(output,'pages.json'),JSON.stringify(rows,null,2));
}
if(rows.length!==pairs.length || rows.some(r=>!r.ok)) process.exitCode=1;

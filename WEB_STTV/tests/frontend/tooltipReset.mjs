/** Exercise the VM's system settings and the persisted, language-independent tooltip records. */
import { chromium } from 'playwright';
import { spawnSync } from 'node:child_process';
import { writeFile } from 'node:fs/promises';

const [base, python, config, report] = process.argv.slice(2);
function ids() {
  const script = [
    'import sys,json','from pathlib import Path','from sttv_loader.settings import settings',
    'from sttv_loader.connection import database',"with database(settings(Path(sys.argv[1]).resolve(),'network')) as db:",
    " print(json.dumps(sorted(db.technology_tooltips.distinct('_id'))))"
  ].join('\n');
  const proc = spawnSync(python,['-B','-c',script,config],{ encoding:'utf8' });
  if(proc.status !== 0) throw Error(proc.stderr);
  return JSON.parse(proc.stdout);
}
function equal(actual, expected) {
  if(JSON.stringify(actual)!==JSON.stringify(expected)) throw Error(JSON.stringify({actual,expected}));
}
const browser = await chromium.launch({executablePath:process.env.STTV_CHROME});
const context = await browser.newContext();
const page = await context.newPage();
const records = [];
try {
  async function clear() {
    await page.getByRole('button',{name:'System settings',exact:true}).click();
    const response=page.waitForResponse(r=>r.request().method()==='DELETE' && r.url().endsWith('/technology-tooltips'));
    await page.getByRole('button',{name:'Reset tooltip content',exact:true}).click();
    equal((await response).status(),200);
    equal(ids(),[]);
  }
  async function open(id,lang,dlc='') {
    const response = page.waitForResponse(r=>r.url().endsWith('/technology-tooltip') &&
      r.request().postDataJSON().language===lang && r.request().postDataJSON().technology_id===id);
    await page.goto(base+'/#/technology/'+id+'?lang='+lang+dlc);
    equal((await response).status(),200);
    await page.locator('article h1').waitFor({timeout:120000});
  }
  page.setDefaultTimeout(120000);
  await open('tech_ordered_retreat','ru','&dlc=');
  await open('tech_lasers_2','en');
  equal(ids(),['tech_lasers_2','tech_ordered_retreat']);
  records.push('two ids with different selectors');
  await clear(); await clear();
  records.push('UI reset and repeated empty reset');
  await open('tech_lasers_2','en');
  equal(ids(),['tech_lasers_2']);
  records.push('first explicit request rebuilt only its own record');
  for(const endpoint of ['research-progress','generated']) {
    equal((await context.request.delete(base+'/api/trees/'+endpoint)).status(),200);
    equal(ids(),[]);
    equal((await context.request.post(base+'/api/trees/technology-tooltip',{data:{technology_id:'tech_lasers_2',language:'en'},timeout:120000})).status(),200);
    equal(ids(),['tech_lasers_2']);
    records.push('reset '+endpoint);
  }
  await writeFile(report, JSON.stringify(records,null,2));
} finally {await browser.close();}

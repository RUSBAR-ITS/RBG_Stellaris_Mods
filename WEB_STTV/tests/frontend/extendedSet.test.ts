import test from 'node:test';
import assert from 'node:assert/strict';
import { sttvAdaptSet } from './setHarness';
import { sttvSet, sttvSetFiles, sttvDataset, sttvAssignment,
  sttvBlock, sttvScalar, sttvLocalization } from './fixtures';
import { sttvDatabaseKinds, type SttvDatabaseKind } from '../../src/frontend/data/registry';
import type { SttvNode } from '../../src/frontend/data/syntax';
import { SttvPreparationError } from '../../src/frontend/workers/diagnostics';

function sttvText(key: string, text: string, role: 'name' | 'description'): SttvNode {
  const localization = sttvLocalization(role === 'name' ? text : text.replace(/_desc$/, ''));
  for (const language of ['ru', 'en'] as const) delete localization[language][role === 'name' ? 'description' : 'name'];
  return { ...sttvAssignment(key, sttvScalar(text)), enrichments: { localization } };
}
function sttvInputs() {
  const values = sttvSet();
  const events = sttvDataset('events', [sttvAssignment('country_event', sttvBlock([
    sttvAssignment('id', sttvScalar('event.1')), sttvText('title', 'heading', 'name'),
    sttvAssignment('desc', sttvBlock([sttvText('text', 'first_desc', 'description'),
      sttvText('text', 'second_desc', 'description')])),
  ])), sttvAssignment('country_event', sttvBlock([sttvAssignment('id', sttvScalar('event.2'))]))]);
  const endpoint = (field: string) => ({ ...sttvAssignment(field, sttvScalar('pc_test')),
    enrichments: { localization: sttvLocalization('pc_test') } });
  const transition = () => sttvAssignment('terraform_link', sttvBlock([endpoint('from'), endpoint('to')]));
  const terraform = sttvDataset('terraform', [transition(), transition()]);
  const handlers = sttvDataset('on_actions', [sttvAssignment('on_day', sttvBlock([])), sttvAssignment('on_day', sttvBlock([]))]);
  for (const db of [events, terraform, handlers]) values[sttvDatabaseKinds.indexOf(db.dataset!.kind as SttvDatabaseKind)] = db;
  return values;
}
test('event descriptions, repeated transitions and handler fragments keep their identities', () => {
  const values = sttvInputs(), catalog = sttvAdaptSet(values, sttvSetFiles(values));
  assert.equal(catalog.definitions.events!.length, 2);
  assert.equal(catalog.definitions.events![0].id, 'event.1');
  assert.equal(catalog.definitions.events![0].type, 'country_event');
  assert.equal(catalog.definitions.events![0].texts.length, 3);
  assert.equal(catalog.definitions.events![1].texts.length, 0);
  assert.equal(catalog.definitions.terraform!.length, 2);
  assert.equal(catalog.definitions.terraform![0].id, undefined);
  assert.equal(catalog.definitions.terraform![0].endpoints!.from.id, 'pc_test');
  assert.equal(catalog.definitionIndex.on_actions!.on_day.length, 2);
  assert.equal(catalog.localization.en.pc_test.origins.length, 4);
  assert.equal(JSON.stringify(catalog).includes('"documents"'), false);
  const reversed = [...values].reverse(), reordered = sttvAdaptSet(reversed, sttvSetFiles(reversed));
  assert.deepEqual(reordered.localization, catalog.localization);
  assert.deepEqual(reordered.definitions, catalog.definitions);
});
test('duplicate event IDs and missing declared texts fail with qualified addresses', () => {
  for (const duplicate of [false, true]) {
    const values = sttvInputs(), items = values.at(-1)!.documents[0].items;
    if (duplicate) items.push(structuredClone(items[0]));
    else delete items[0].value!.items![1].enrichments;
    assert.throws(() => sttvAdaptSet(values, sttvSetFiles(values)), SttvPreparationError);
  }
});
test('metadata rejects wrong counts, duplicate or unknown roles, reports and version five', () => {
  for (const mode of ['14', '16', 'duplicate', 'unknown', 'report', 'version']) {
    const values = sttvSet();
    if (mode === '14') values.pop();
    if (mode === '16') values.push(values[0]);
    if (mode === 'duplicate') values[14] = values[0];
    if (mode === 'unknown') values[14].dataset!.kind = 'unknown' as never;
    if (mode === 'report') values[14].format = 'sttv.database_set_report';
    if (mode === 'version') values[14].format_version = 5;
    assert.throws(() => sttvAdaptSet(values, sttvSetFiles(values)), SttvPreparationError, mode);
  }
});

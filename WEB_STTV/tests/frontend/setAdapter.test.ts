import test from 'node:test';
import assert from 'node:assert/strict';
import { sttvAdaptSet } from './setHarness';
import { SttvPreparationError } from '../../src/frontend/workers/diagnostics';
import { sttvAssignment, sttvBlock, sttvDatabase, sttvDataset, sttvLocalization,
  sttvLogical, sttvScalar, sttvSet, sttvSetFiles, sttvTechnology } from './fixtures';
import type { SttvNode } from '../../src/frontend/data/syntax';

function sttvComponent(id: string, tech: string, upgrade?: string): SttvNode {
  return { ...sttvAssignment('utility_component_template', sttvBlock([
    sttvAssignment('key', sttvScalar(id)), sttvAssignment('prerequisites', sttvBlock([sttvScalar(tech)])),
    ...(upgrade ? [sttvAssignment('upgrades_to', sttvScalar(upgrade))] : []),
  ])), enrichments: { localization: sttvLocalization(id) } };
}
function sttvBuilding(id: string, tech: string, upgrade?: string): SttvNode {
  return { ...sttvAssignment(id, sttvBlock([
    sttvAssignment('prerequisites', sttvBlock([sttvScalar(tech)])),
    ...(upgrade ? [sttvAssignment('upgrades', sttvBlock([sttvScalar(upgrade)]))] : []),
  ])), enrichments: { localization: sttvLocalization(id) } };
}
function sttvInputs() {
  const result = sttvSet(sttvDatabase([sttvTechnology('a'), sttvTechnology('b', 1, 'physics', [sttvScalar('a')])]));
  result[1] = sttvDataset('components', [sttvComponent('shared', 'a', 'second'), sttvComponent('second', 'b')]);
  result[2] = sttvDataset('buildings', [sttvBuilding('shared', 'a', 'second'), sttvBuilding('second', 'b')]);
  return result;
}
test('roles come from metadata; identical IDs and pointers in different databases remain distinct', () => {
  const inputs = sttvInputs().reverse();
  const result = sttvAdaptSet(inputs, sttvSetFiles(inputs));
  assert.equal(result.datasets[0].kind, 'events');
  assert.equal(result.components.shared.sourceRef.database, 'components');
  assert.equal(result.buildings.shared.sourceRef.database, 'buildings');
  assert.equal(result.localization.ru.shared.origins.length, 2);
  assert.deepEqual(result.localization.ru.shared.origins.map(origin => origin.recordRef.database), ['components', 'buildings']);
  assert.equal(result.links.length, 1);
  assert.equal(result.objectRequirements.length, 4);
  assert.equal(result.objectUpgrades.length, 2);
  assert.equal(result.upgradeEvidence.length, 1);
  assert.equal(result.upgradeEvidence[0].witnesses.length, 2);
});
test('incomplete, duplicate-role, mixed and old sets are rejected', () => {
  const mixed = sttvInputs(); mixed[2].dataset!.set_id = 'b'.repeat(64);
  const old = sttvInputs(); old[1].format_version = 4;
  const missing = sttvInputs(); delete missing[2].dataset;
  for (const inputs of [sttvInputs().slice(1), [sttvInputs()[0], sttvInputs()[0], sttvInputs()[2]], mixed, old, missing]) {
    assert.throws(() => sttvAdaptSet(inputs, sttvSetFiles(inputs)), SttvPreparationError);
  }
});
test('conditional descriptions and component fallback retain qualified origins', () => {
  const inputs = sttvInputs();
  const building = inputs[2].documents[0].items[0];
  const localization = sttvLocalization('unused');
  for (const language of ['ru', 'en'] as const) delete localization[language].name;
  building.value!.items!.push({ ...sttvAssignment('desc', sttvBlock([
    sttvAssignment('trigger', sttvBlock([])), sttvAssignment('text', sttvScalar('unused_desc')),
  ])), enrichments: { localization } });
  const component = inputs[1].documents[0].items[0];
  component.enrichments!.localization!.ru.description!.fallback = {
    kind: 'component_set', source_ref: '/documents/0/items/0/value/items/3' };
  const catalog = sttvAdaptSet(inputs, sttvSetFiles());
  assert.deepEqual(catalog.buildings.shared.conditionalDescriptions[0].triggerRef,
    { database: 'buildings', pointer: '/documents/0/items/0/value/items/2/value/items/0/value' });
  assert.equal(catalog.localization.ru.unused_desc.origins[0].recordRef.database, 'buildings');
  assert.equal(catalog.localization.ru.shared_desc.origins[0].fallback?.sourceRef.database, 'components');
});
test('negative object requirements survive without layout counting or invented evidence', () => {
  const inputs = sttvInputs();
  const values = inputs[1].documents[0].items[1].value!.items![1].value!.items!;
  values.splice(0, values.length, sttvLogical('NOT', [sttvScalar('b')]));
  const catalog = sttvAdaptSet(inputs, sttvSetFiles());
  assert.equal(catalog.components.second.prerequisites.items[0].kind, 'group');
  assert.equal(catalog.upgradeEvidence[0].witnesses.length, 1);
  assert.equal(catalog.upgradeEvidence[0].witnesses[0].upgrade.from.database, 'buildings');
});
test('upgrade hints require an existing technology prerequisite and do not create links', () => {
  const inputs = sttvInputs();
  inputs[0] = sttvDataset('technologies', [sttvTechnology('a'), sttvTechnology('b')]);
  const catalog = sttvAdaptSet(inputs, sttvSetFiles());
  assert.equal(catalog.objectUpgrades.length, 2);
  assert.deepEqual(catalog.upgradeEvidence, []);
  assert.deepEqual(catalog.links, []);
});
test('unresolved cross references and duplicate object IDs fail with database-qualified locations', () => {
  for (const mode of ['technology', 'upgrade', 'duplicate']) {
    const inputs = sttvInputs();
    const items = inputs[1].documents[0].items;
    if (mode === 'duplicate') items.push(structuredClone(items[0]));
    if (mode === 'upgrade') items.pop();
    if (mode === 'technology') inputs[0].documents[0].items.pop();
    assert.throws(() => sttvAdaptSet(inputs, sttvSetFiles()), (error: unknown) => {
      assert.ok(error instanceof SttvPreparationError);
      assert.equal((error.diagnostic.details.sourceRef as { database: string }).database, 'components');
      return true;
    });
  }
});
test('cross-database localization conflicts retain both origins and stop preparation', () => {
  const inputs = sttvInputs();
  inputs[2].documents[0].items[0].enrichments!.localization!.ru.name!.text = 'Conflicting name';
  assert.throws(() => sttvAdaptSet(inputs, sttvSetFiles()), (error: unknown) => {
    assert.ok(error instanceof SttvPreparationError);
    assert.equal(error.diagnostic.code, 'localization_conflict');
    const details = JSON.stringify(error.diagnostic.details);
    assert.ok(details.includes('components') && details.includes('buildings'));
    return true;
  });
});

test('missing object enrichment and ambiguous transformation fields stop opening', () => {
  for (const mode of ['localization', 'identity']) {
    const inputs = sttvInputs();
    const node = inputs[1].documents[0].items[0];
    if (mode === 'localization') delete node.enrichments;
    else node.value!.items!.push(sttvAssignment('key', sttvScalar('duplicate')));
    assert.throws(() => sttvAdaptSet(inputs, sttvSetFiles()), SttvPreparationError);
  }
});

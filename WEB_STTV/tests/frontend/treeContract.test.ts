import test from 'node:test';
import assert from 'node:assert/strict';
import { sttvAdaptDatabase } from '../../src/frontend/data/adapter';
import { sttvTreeCombination } from '../../src/frontend/data/tree/metadata';
import { sttvValidateTree } from '../../src/frontend/data/tree/validation';
import { SttvPreparationError } from '../../src/frontend/workers/diagnostics';
import { sttvDatabase, sttvSet, sttvTechnology } from './fixtures';
import { sttvBundle } from './manifestFixtures';
import { sttvCombination, sttvConnect } from './treeFixtures';

test('combination metadata distinguishes absence, stale inputs and malformed contracts', () => {
  const { manifest } = sttvBundle(sttvSet());
  const original = structuredClone(manifest);
  const check = (change: (m: any) => void, code: string) => {
    const modified = structuredClone(original); change(modified);
    assert.throws(() => sttvTreeCombination(modified), (e: unknown) => e instanceof SttvPreparationError && e.diagnostic.code === code);
  };
  check(m => delete m.technology_tree, 'tree_combination_missing');
  check(m => m.technology_tree.format_version = 2, 'tree_combination_missing');
  check(m => m.technology_tree.combinations.reference_default.source_set_id = 'x', 'tree_combination_stale');
  check(m => m.technology_tree.combinations.reference_default.inputs[0].hash = 'x', 'tree_combination_stale');
  check(m => m.technology_tree.combinations.reference_default.parameters.variants = [], 'tree_enrichment_invalid');
  check(m => m.technology_tree.combinations.reference_default.inputs = [], 'tree_enrichment_invalid');
  check(m => delete m.technology_tree.combinations.reference_default.result_revision, 'tree_enrichment_invalid');
  assert.equal(sttvTreeCombination(manifest).id, 'reference_default');
});

test('missing record, repeated children and invalid status are not interpreted as roots', () => {
  for (const row of [undefined, { parent_tech: null, children: ['a', 'a'], status: 'root' },
    { parent_tech: null, children: [], status: 'resolved' }, { parent_tech: null, children: [], status: 'unknown' }]) {
    const node = sttvTechnology('a'); node.enrichments.technology_tree = row === undefined ? {} as any : { reference_default: row } as any;
    assert.throws(() => sttvAdaptDatabase(sttvDatabase([node])), SttvPreparationError);
  }
});

test('graph contract detects unknown variants, nonreciprocal links, unknown parents and cross-area cycles', () => {
  const make = () => {
    const nodes = [sttvTechnology('a'), sttvTechnology('b', 1, 'society')]; sttvConnect(nodes, { b: 'a' });
    return { ...sttvAdaptDatabase(sttvDatabase(nodes)), combination: sttvCombination(['a', 'b']) };
  };
  for (const mutate of [
    (d: ReturnType<typeof make>) => { delete d.combination.parameters.variants.a; },
    (d: ReturnType<typeof make>) => { d.combination.parameters.variants.a = 'swap:99'; },
    (d: ReturnType<typeof make>) => { d.combination.parameters.variants.unknown = 'base'; },
    (d: ReturnType<typeof make>) => { d.technologies.a.tree.children = []; },
    (d: ReturnType<typeof make>) => { d.technologies.b.tree.parent_tech = 'unknown'; },
    (d: ReturnType<typeof make>) => { d.technologies.a.tree = { parent_tech: 'b', children: ['b'], status: 'resolved' };
      d.technologies.b.tree.children = ['a']; },
  ]) { const data = make(); mutate(data); assert.throws(() => sttvValidateTree(data.technologies, data.combination), SttvPreparationError); }
});

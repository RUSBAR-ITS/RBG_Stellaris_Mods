import { sttvSet, sttvDatabase, sttvTechnology, sttvAssignment as a, sttvBlock as b,
  sttvScalar as s, sttvLocalization } from './fixtures';

export function sttvDlcFixture() {
  const parent = sttvTechnology('parent'), child = sttvTechnology('child', 1, 'physics', [s('parent')]);
  parent.enrichments.technology_tree.reference_default.children = ['child'];
  Object.assign(child.enrichments.technology_tree.reference_default, { parent_tech: 'parent', status: 'resolved' });
  const inputs = sttvSet(sttvDatabase([parent, child]));
  inputs.find(d => d.database === 'dlcs')!.items = [a('dlcs', b(['a', 'b'].map(id => ({
    ...a(id, b([a('name', s(id))])), enrichments: { localization: sttvLocalization(id, `DLC ${id}`) },
  }))))];
  return inputs;
}


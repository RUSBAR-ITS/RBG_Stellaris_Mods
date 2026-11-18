import type { SttvNode } from './syntax';
import { sttvItems, sttvScalar } from './syntax';
import type { SttvGroup, SttvLink, SttvOperator, SttvRequirement } from './model';
import { sttvInvalid } from '../workers/diagnostics';

function sttvReadRequirement(node: SttvNode, path: string, allowNegative: boolean): SttvRequirement {
  if (node.kind === 'scalar') return { kind: 'technology', technologyId: sttvScalar(node, path) };
  if (node.kind === 'logical_operation') {
    const operator = node.operator as SttvOperator;
    if (!['AND', 'OR', 'NOT', 'NAND', 'NOR'].includes(operator)) throw sttvInvalid(path, 'Unknown logical operator.');
    if (!allowNegative && ['NOT', 'NAND', 'NOR'].includes(operator)) {
      throw sttvInvalid(path, `Counting and layout for ${operator} require a separate agreed rule.`);
    }
    const children = node.body?.kind === 'block' ? sttvItems(node.body, path) : [node.body!];
    return { kind: 'group', operator,
      items: children.map((item, i) => sttvReadRequirement(item,
        node.body?.kind === 'block' ? `${path}/body/items/${i}` : `${path}/body`, allowNegative)) };
  }
  throw sttvInvalid(path, 'Unsupported technology requirement shape.');
}
export function sttvRequirementCount(node: SttvRequirement): number {
  if (node.kind === 'technology') return 1;
  if (node.operator !== 'AND' && node.operator !== 'OR') {
    throw sttvInvalid('/prerequisites', `Counting ${node.operator} requires a separate agreed rule.`);
  }
  const counts = node.items.map(sttvRequirementCount);
  return node.operator === 'OR' ? 1 : counts.reduce((sum, count) => sum + count, 0);
}
export function sttvRequirements(value: SttvNode | undefined, sourceRef: string, id: string) {
  const result = sttvReadRequirements(value, sourceRef, id);
  return { ...result, requirementCount: sttvRequirementCount(result.prerequisites) };
}
export function sttvReadRequirements(value: SttvNode | undefined, sourceRef: string, id: string, allowNegative = false) {
  const items = value ? sttvItems(value, sourceRef) : [];
  const prerequisites: SttvGroup = { kind: 'group', operator: 'AND',
    items: items.map((node, i) => sttvReadRequirement(node, `${sourceRef}/items/${i}`, allowNegative)) };
  const byId = new Map<string, SttvLink>();
  function visit(node: SttvRequirement, path: number[]) {
    if (node.kind === 'group') node.items.forEach((child, i) => visit(child, [...path, i]));
    else {
      let link = byId.get(node.technologyId);
      if (!link) { link = { from: node.technologyId, to: id, requirementPaths: [] }; byId.set(link.from, link); }
      link.requirementPaths.push(path);
    }
  }
  visit(prerequisites, []);
  return { prerequisites, prerequisiteIds: [...byId.keys()],
    links: [...byId.values()] };
}

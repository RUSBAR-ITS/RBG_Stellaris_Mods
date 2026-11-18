import type { SttvCatalog, SttvObject, SttvUpgradeEvidence } from './model';
import { sttvInvalid } from '../workers/diagnostics';

function sttvSingleRequirement(object: SttvObject) {
  const items = object.prerequisites.items;
  return items.length === 1 && items[0].kind === 'technology' ? items[0].technologyId : null;
}
export function sttvUpgradeEvidence(catalog: SttvCatalog) {
  const evidence = new Map<string, SttvUpgradeEvidence>();
  for (const requirement of catalog.objectRequirements) {
    if (!catalog.technologies[requirement.from.id]) {
      throw sttvInvalid(requirement.sourceRef, `Unresolved technology: ${requirement.from.id}`);
    }
  }
  for (const upgrade of catalog.objectUpgrades) {
    const objects = upgrade.from.database === 'components' ? catalog.components : catalog.buildings;
    const from = objects[upgrade.from.id], to = objects[upgrade.to.id];
    if (!to) throw sttvInvalid(upgrade.sourceRef, `Unresolved ${upgrade.to.database} upgrade: ${upgrade.to.id}`);
    const predecessor = sttvSingleRequirement(from), successor = sttvSingleRequirement(to);
    if (!predecessor || !successor || predecessor === successor
      || !catalog.technologies[successor].prerequisiteIds.includes(predecessor)) continue;
    const key = JSON.stringify([predecessor, successor]);
    if (!evidence.has(key)) evidence.set(key, { from: predecessor, to: successor, witnesses: [] });
    evidence.get(key)!.witnesses.push({ upgrade,
      fromPrerequisitesRef: from.prerequisitesRef!, toPrerequisitesRef: to.prerequisitesRef! });
  }
  return [...evidence.values()];
}

import type { SttvCatalog, SttvNodeRef, SttvTechnologyCatalog } from './model';
import type { SttvDatabase } from './syntax';
import { SttvSetMetadata } from './setMetadata';
import { sttvAdaptDatabase, sttvValidateTechnologies } from './adapter';
import { sttvAdaptObjects } from './objects';
import { sttvAdaptDefinitions } from './definitions';
import { sttvUpgradeEvidence } from './upgradeEvidence';
import { SttvIndexBuilder } from '../localization/index';
import { SttvPreparationError, sttvInvalid, type SttvDiagnostic } from '../workers/diagnostics';
import type { SttvTargetRegistry } from './textTargets';

export class SttvSetAdapter {
  readonly metadata: SttvSetMetadata;
  readonly strings = new SttvIndexBuilder();
  private technologies: SttvTechnologyCatalog | null = null;
  private components: ReturnType<typeof sttvAdaptObjects> | null = null;
  private buildings: ReturnType<typeof sttvAdaptObjects> | null = null;
  private definitions: SttvCatalog['definitions'] = {};
  private definitionIndex: SttvCatalog['definitionIndex'] = {};
  constructor(files: { name: string; size: number }[], private rules: SttvTargetRegistry,
    private diagnostics: SttvDiagnostic[] = []) { this.metadata = new SttvSetMetadata(files); }

  begin(input: unknown, fileIndex: number) {
    const member = this.metadata.add(input, fileIndex);
    const database = member.kind;
    if (database === 'technologies') this.technologies = { technologies: Object.create(null), links: [],
      localization: this.strings.index, diagnostics: [] };
    else if (database === 'components' || database === 'buildings') {
      this[database] = { objects: Object.create(null), requirements: [], upgrades: [] };
    } else {
      this.definitions[database] = []; this.definitionIndex[database] = Object.create(null);
    }
    return member;
  }
  document(input: unknown, fileIndex: number, documentOffset: number) {
    const member = this.metadata.datasets.find(item => item.fileIndex === fileIndex)!;
    const db = input as SttvDatabase, database = member.kind;
    try {
      if (database === 'technologies') sttvAdaptDatabase(db, [], this.strings, false,
        { catalog: this.technologies!, documentOffset });
      else if (database === 'components' || database === 'buildings') sttvAdaptObjects(db, database, this.strings,
        { catalog: this[database]!, documentOffset });
      else {
        const rules = this.rules[database];
        if (!rules) throw sttvInvalid({ database, pointer: '' }, 'Localization target rules are missing.');
        sttvAdaptDefinitions(db, database, rules, this.strings, { documentOffset,
          definitions: this.definitions[database]!, index: this.definitionIndex[database]! });
      }
      return member;
    } catch (error) {
      if (error instanceof SttvPreparationError) {
        const details = error.diagnostic.details;
        if (typeof details.path === 'string') {
          details.sourceRef ??= { database, pointer: details.path };
          delete details.path;
        }
        const source = details.sourceRef as SttvNodeRef | undefined;
        const indices = source?.pointer.match(/^\/documents\/(\d+)\/items\/(\d+)/);
        if (source && indices) {
          const document = db.documents[Number(indices[1]) - documentOffset];
          details.sourceFile = document?.source.file;
        }
      }
      throw error;
    }
  }
  add(input: unknown, fileIndex: number) {
    const member = this.begin(input, fileIndex), db = input as SttvDatabase;
    db.documents.forEach((document, index) => this.document({ ...db, documents: [document] }, fileIndex, index));
    return member;
  }
  finish(): SttvCatalog {
    this.metadata.finish();
    if (!this.technologies || !this.components || !this.buildings) throw sttvInvalid('', 'Core catalogs are missing.');
    sttvValidateTechnologies(this.technologies);
    this.strings.orderOrigins();
    const catalog: SttvCatalog = { ...this.technologies,
      setId: this.metadata.setId, datasets: this.metadata.datasets, diagnostics: this.diagnostics,
      components: this.components.objects, buildings: this.buildings.objects,
      objectRequirements: [...this.components.requirements, ...this.buildings.requirements],
      objectUpgrades: [...this.components.upgrades, ...this.buildings.upgrades], upgradeEvidence: [],
      definitions: this.definitions, definitionIndex: this.definitionIndex };
    catalog.upgradeEvidence = sttvUpgradeEvidence(catalog);
    this.diagnostics.push(...this.strings.warnings());
    return catalog;
  }
}

export function sttvAdaptSet(inputs: unknown[], files: { name: string; size: number }[],
  rules: SttvTargetRegistry, diagnostics: SttvDiagnostic[] = []): SttvCatalog {
  const adapter = new SttvSetAdapter(files, rules, diagnostics);
  inputs.forEach((input, i) => adapter.add(input, i));
  return adapter.finish();
}

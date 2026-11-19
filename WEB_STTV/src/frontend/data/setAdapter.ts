import type { SttvCatalog, SttvDatabaseKind, SttvTechnologyCatalog, SttvObjectCatalog } from './model';
import type { SttvDatabase } from './syntax';
import type { SttvManifest, SttvCoverage } from '../storage/model';
import { sttvAdaptDatabase, sttvValidateTechnologies } from './adapter';
import { sttvAdaptObjects } from './objects';
import { sttvAdaptDefinitions } from './definitions';
import { sttvUpgradeEvidence } from './upgradeEvidence';
import { sttvDatabaseKinds } from './registry';
import { SttvIndexBuilder } from '../localization/index';
import { SttvPreparationError, sttvInvalid, type SttvDiagnostic } from '../workers/diagnostics';
import type { SttvTargetRegistry } from './textTargets';

export class SttvSetAdapter {
  strings = new SttvIndexBuilder();
  technologies: SttvTechnologyCatalog = { technologies: Object.create(null), links: [],
    localization: this.strings.index, diagnostics: [] };
  components: SttvObjectCatalog = { objects: Object.create(null), requirements: [], upgrades: [] };
  buildings: SttvObjectCatalog = { objects: Object.create(null), requirements: [], upgrades: [] };
  definitions: SttvCatalog['definitions'] = {};
  definitionIndex: SttvCatalog['definitionIndex'] = {};
  loadedDocuments = new Set<string>();
  datasets: SttvCatalog['datasets'];
  constructor(readonly manifest: SttvManifest, private rules: SttvTargetRegistry,
    private diagnostics: SttvDiagnostic[] = []) {
    this.datasets = sttvDatabaseKinds.map(kind => ({ kind, name: kind,
      size: manifest.datasets[kind].documents.reduce((sum, d) => sum + d.byte_size, 0),
      documentCount: manifest.datasets[kind].documents.length,
      objectCount: manifest.datasets[kind].objects.length, state: 'not_loaded' }));
  }
  fork() {
    const copy = new SttvSetAdapter(this.manifest, this.rules, [...this.diagnostics]);
    copy.strings = this.strings.fork();
    for (const field of ['technologies', 'components', 'buildings', 'definitions', 'definitionIndex', 'datasets'] as const) {
      Object.assign(copy, { [field]: structuredClone(this[field]) });
    }
    copy.technologies.localization = copy.strings.index;
    for (const dictionary of [copy.technologies.technologies, copy.components.objects, copy.buildings.objects,
      copy.definitions, copy.definitionIndex, ...Object.values(copy.definitionIndex)]) Object.setPrototypeOf(dictionary, null);
    copy.loadedDocuments = new Set(this.loadedDocuments);
    return copy;
  }
  document(db: SttvDatabase, itemOffset: number) {
    const database = db.database;
    try {
      if (database === 'technologies') sttvAdaptDatabase(db, [], this.strings, false,
        { catalog: this.technologies, itemOffset });
      else if (database === 'components' || database === 'buildings') sttvAdaptObjects(db, database, this.strings,
        { catalog: this[database], itemOffset });
      else {
        const rules = this.rules[database];
        if (!rules) throw sttvInvalid('', 'Localization target rules are missing.');
        this.definitions[database] ??= []; this.definitionIndex[database] ??= Object.create(null);
        sttvAdaptDefinitions(db, database, rules, this.strings, { itemOffset,
          definitions: this.definitions[database]!, index: this.definitionIndex[database]! });
      }
    } catch (error) {
      if (error instanceof SttvPreparationError) {
        const details = error.diagnostic.details;
        if (typeof details.path === 'string') {
          details.sourceRef ??= { database, document_id: db.document_id, pointer: details.path };
          delete details.path;
        }
        details.sourceFile ??= db.source.file;
      }
      throw error;
    }
  }
  completed(kind: SttvDatabaseKind, identifier: string) {
    this.loadedDocuments.add(identifier);
    if (this.manifest.datasets[kind].documents.every(row => this.loadedDocuments.has(row.document_id))) {
      this.datasets.find(row => row.kind === kind)!.state = 'loaded';
    }
  }
  finish(coverage: SttvCoverage): SttvCatalog {
    if (this.datasets.find(row => row.kind === 'technologies')!.state === 'loaded') sttvValidateTechnologies(this.technologies);
    this.strings.orderOrigins();
    const loaded = (kind: SttvDatabaseKind) => this.datasets.find(row => row.kind === kind)!.state === 'loaded';
    const catalog: SttvCatalog = { ...this.technologies,
      localization: this.strings.index, setId: this.manifest.set_id, snapshotRevision: this.manifest.snapshot_revision,
      datasets: this.datasets, diagnostics: [...this.diagnostics, ...this.strings.warnings()], coverage,
      components: this.components.objects, buildings: this.buildings.objects,
      objectRequirements: [...(loaded('components') ? this.components.requirements : []),
        ...(loaded('buildings') ? this.buildings.requirements : [])],
      objectUpgrades: [...(loaded('components') ? this.components.upgrades : []),
        ...(loaded('buildings') ? this.buildings.upgrades : [])], upgradeEvidence: [],
      definitions: this.definitions, definitionIndex: this.definitionIndex };
    if (loaded('technologies')) catalog.upgradeEvidence = sttvUpgradeEvidence(catalog);
    return catalog;
  }
}

import type { SttvCatalog, SttvDatabaseKind, SttvTechnologyCatalog, SttvObjectCatalog } from './model';
import type { SttvDatabase } from './syntax';
import type { SttvManifest, SttvCoverage } from '../storage/model';
import { sttvAdaptDatabase, sttvValidateTechnologies } from './adapter';
import { sttvAdaptObjects } from './objects';
import { sttvAdaptDefinitions } from './definitions';
import { sttvUpgradeEvidence } from './upgradeEvidence';
import { sttvDatabaseKinds } from './registry';
import { sttvSetError } from './setMetadata';
import { SttvIndexBuilder } from '../localization/index';
import { SttvPreparationError, sttvInvalid, type SttvDiagnostic } from '../workers/diagnostics';
import type { SttvTargetRegistry } from './textTargets';
import { sttvTreeCombination } from './tree/metadata';
import { sttvValidateTree } from './tree/validation';
import layoutSettings from '../../../config/frontend/tree_layout.json';
import { sttvTreeRecord } from './tree/extraction';
import type { SttvTreeRecord } from './tree/model';

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
  treeCombination: SttvCatalog['treeCombination'];
  private savedTrees: Record<string, Record<string, SttvTreeRecord>> = Object.create(null);
  constructor(readonly manifest: SttvManifest, private rules: SttvTargetRegistry,
    private diagnostics: SttvDiagnostic[] = [], private combinationId = layoutSettings.combination_id) {
    this.treeCombination = sttvTreeCombination(manifest, combinationId);
    this.datasets = sttvDatabaseKinds.map(kind => ({ kind, name: kind,
      size: manifest.datasets[kind].documents.reduce((sum, d) => sum + d.byte_size, 0),
      documentCount: manifest.datasets[kind].documents.length,
      objectCount: manifest.datasets[kind].objects.length, state: 'not_loaded' }));
  }
  fork(manifest = this.manifest, combinationId = this.combinationId) {
    const copy = new SttvSetAdapter(manifest, this.rules, [...this.diagnostics], combinationId);
    copy.strings = this.strings.fork();
    for (const field of ['technologies', 'components', 'buildings', 'definitions', 'definitionIndex', 'datasets'] as const) {
      Object.assign(copy, { [field]: structuredClone(this[field]) });
    }
    copy.technologies.localization = copy.strings.index;
    for (const dictionary of [copy.technologies.technologies, copy.components.objects, copy.buildings.objects,
      copy.definitions, copy.definitionIndex, ...Object.values(copy.definitionIndex)]) Object.setPrototypeOf(dictionary, null);
    copy.loadedDocuments = new Set(this.loadedDocuments);
    copy.savedTrees = structuredClone(this.savedTrees);
    return copy;
  }
  rebase(manifest: SttvManifest, combinationId: string) {
    if (manifest.set_id !== this.manifest.set_id) sttvSetError('Cannot attach a snapshot from another source set.');
    const changed = new Set<string>();
    for (const kind of sttvDatabaseKinds) for (const row of manifest.datasets[kind].documents) {
      const old = this.manifest.datasets[kind].documents.find(d => d.document_id === row.document_id);
      if (!old || old.source_hash !== row.source_hash) sttvSetError('Source documents changed during DLC calculation.');
      if (old.file_hash !== row.file_hash) {
        if (kind !== 'technologies') sttvSetError('Unexpected changed dataset in a tree operation.', { kind });
        changed.add(row.document_id);
      }
    }
    const copy = this.fork(manifest, combinationId);
    copy.strings.removeDocuments(changed);
    for (const [id, tech] of Object.entries(copy.technologies.technologies)) {
      if (changed.has(tech.sourceRef.document_id)) { delete copy.technologies.technologies[id]; delete copy.savedTrees[id]; }
      else tech.tree = sttvTreeRecord(copy.savedTrees[id], combinationId, tech.sourceRef);
    }
    copy.technologies.links = copy.technologies.links.filter(link => !!copy.technologies.technologies[link.to]);
    copy.diagnostics = copy.diagnostics.filter(d => !changed.has(String((d.details.sourceRef as { document_id?: string })?.document_id)));
    for (const id of changed) copy.loadedDocuments.delete(id);
    copy.datasets = copy.datasets.map(d => ({ ...d, state: manifest.datasets[d.kind].documents.every(row => copy.loadedDocuments.has(row.document_id))
      ? 'loaded' : d.state === 'loaded' ? 'not_loaded' : d.state }));
    return copy;
  }
  document(db: SttvDatabase, itemOffset: number) {
    const database = db.database;
    try {
      if (database === 'technologies') {
        sttvAdaptDatabase(db, this.diagnostics, this.strings, false,
          { catalog: this.technologies, itemOffset, combinationId: this.combinationId });
        for (const node of db.items) {
          const id = node.key?.text, tech = id && this.technologies.technologies[id];
          if (tech && node.enrichments?.technology_tree) {
            this.savedTrees[id!] = Object.fromEntries(Object.keys(node.enrichments.technology_tree).map(combo =>
              [combo, sttvTreeRecord(node.enrichments!.technology_tree, combo, tech.sourceRef)]));
          }
        }
      }
      else if (database === 'components' || database === 'buildings') sttvAdaptObjects(db, database, this.strings,
        { catalog: this[database], itemOffset });
      else {
        const rules = this.rules[database];
        if (!rules) throw sttvInvalid('', 'Localization target rules are missing.');
        this.definitions[database] ??= []; this.definitionIndex[database] ??= Object.create(null);
        sttvAdaptDefinitions(db, database, rules, this.strings, { itemOffset,
          definitions: this.definitions[database]!, index: this.definitionIndex[database]! });
        for (const definition of this.definitions[database]!) for (const ref of definition.descriptorRefs ?? []) {
          if (ref.database !== 'dlcs' || !this.manifest.datasets.dlcs.documents.some(row => row.document_id === ref.document_id)) {
            throw sttvInvalid(definition.sourceRef, 'DLC descriptor reference leaves the declared dataset.');
          }
        }
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
    if (this.datasets.find(row => row.kind === 'technologies')!.state === 'loaded') {
      sttvValidateTechnologies(this.technologies);
      sttvValidateTree(this.technologies.technologies, this.treeCombination);
    }
    this.strings.orderOrigins();
    const loaded = (kind: SttvDatabaseKind) => this.datasets.find(row => row.kind === kind)!.state === 'loaded';
    const catalog: SttvCatalog = { ...this.technologies, treeCombination: this.treeCombination,
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

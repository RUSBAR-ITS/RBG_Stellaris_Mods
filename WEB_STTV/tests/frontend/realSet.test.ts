import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, statSync, writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { openAsBlob } from 'node:fs';
import { sttvReadJson } from '../../src/frontend/data/jsonStream';
import { SttvSetAdapter } from '../../src/frontend/data/setAdapter';
import { sttvDatabaseKinds } from '../../src/frontend/data/registry';
import { sttvRules } from './setHarness';

test('real set preserves catalogs and confirms previously researched upgrade witnesses', { skip: !process.env.STTV_DATABASE_DIR }, async () => {
  const directory = process.env.STTV_DATABASE_DIR ?? 'data/databases';
  const kinds = [...sttvDatabaseKinds].reverse();
  const files = kinds.map(kind => ({ name: `${kind}.json`, size: statSync(join(directory, `${kind}.json`)).size }));
  const started = performance.now();
  const adapter = new SttvSetAdapter(files, sttvRules);
  for (const [index, file] of files.entries()) {
    const blob = await openAsBlob(join(directory, file.name));
    const { metadata, documentCount } = await sttvReadJson(blob);
    adapter.begin(metadata, index);
    adapter.metadata.datasets.at(-1)!.documentCount = documentCount;
    await sttvReadJson(blob, (document, offset) => adapter.document({ ...metadata, documents: [document] }, index, offset));
  }
  const catalog = adapter.finish();
  assert.equal(catalog.datasets.length, 15);
  assert.equal(Object.keys(catalog.technologies).length, 679);
  assert.equal(Object.keys(catalog.components).length, 1506);
  assert.equal(Object.keys(catalog.buildings).length, 498);
  const research = JSON.parse(readFileSync('data/chain_analysis/unlock_evidence.json', 'utf8'));
  const existing = new Map(catalog.upgradeEvidence.map(item => [`${item.from}:${item.to}`, item]));
  for (const expected of research.evidence) {
    const found = existing.get(`${expected.from_tech}:${expected.to_tech}`);
    assert.ok(found, `${expected.from_tech} -> ${expected.to_tech}`);
    assert.ok(found.witnesses.some(witness => witness.upgrade.from.id === expected.from.key
      && witness.upgrade.to.id === expected.to.key), `${expected.from.key} -> ${expected.to.key}`);
  }
  const afterburners = existing.get('tech_afterburners_1:tech_afterburners_2');
  assert.ok(afterburners?.witnesses.some(item => item.upgrade.from.id === 'AFTERBURNER_1'));
  assert.ok(catalog.technologies.tech_afterburners_2.prerequisiteIds.includes('tech_thrusters_3'));
  const text = JSON.stringify(catalog);
  assert.equal(text.includes('"documents"'), false);
  const report = { technologies: Object.keys(catalog.technologies).length,
    definitions: Object.fromEntries(Object.entries(catalog.definitions).map(([kind, rows]) => [kind, rows.length])),
    components: Object.keys(catalog.components).length, buildings: Object.keys(catalog.buildings).length,
    conditionalDescriptions: Object.values(catalog.buildings).reduce((n, item) => n + item.conditionalDescriptions.length, 0),
    links: catalog.links.length, objectRequirements: catalog.objectRequirements.length,
    objectUpgrades: catalog.objectUpgrades.length, upgradePairs: catalog.upgradeEvidence.length,
    upgradeWitnesses: catalog.upgradeEvidence.reduce((n, item) => n + item.witnesses.length, 0),
    confirmedResearchCases: new Set(research.evidence.map((item: { to_tech: string }) => item.to_tech)).size,
    confirmedResearchWitnesses: research.evidence.length, mainThreadBytes: Buffer.byteLength(text),
    seconds: (performance.now() - started) / 1000, warnings: catalog.diagnostics.length,
    warningsByCode: catalog.diagnostics.reduce((counts, item) => {
      counts[item.code] = (counts[item.code] ?? 0) + 1; return counts;
    }, {} as Record<string, number>) };
  mkdirSync('data/stage12', { recursive: true });
  writeFileSync('data/stage12/frontend_catalog_report.json', JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report));
});

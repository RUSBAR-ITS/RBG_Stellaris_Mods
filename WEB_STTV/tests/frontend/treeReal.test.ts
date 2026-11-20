import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { SttvStorageSession } from '../../src/frontend/storage/session';
import { sttvLayout } from '../../src/frontend/data/tree/layout';
import settings from '../../config/frontend/tree_layout.json' with { type: 'json' };
import { sttvRealFiles } from './realFiles';
import { sttvRules } from './setHarness';

test('prepared real combinations cover all technologies without rereads, mutations or overlaps',
  { skip: !process.env.STTV_DATABASE_DIR }, async () => {
    const directory = process.env.STTV_DATABASE_DIR!, manifestPath = join(directory, 'manifest.json');
    const manifestBytes = readFileSync(manifestPath), manifest = JSON.parse(manifestBytes.toString());
    const docs = Object.values(manifest.datasets).flatMap((d: any) => d.documents) as { path: string }[];
    const stats = docs.map(doc => statSync(join(directory, doc.path)).mtimeMs);
    const reports = [];
    for (const combinationId of ['reference_default', 'reference_variants']) {
      const files = await sttvRealFiles(directory), readCounts = new Map<string, number>();
      for (const file of files) {
        const stream = file.stream.bind(file);
        file.stream = () => { readCounts.set(file.webkitRelativePath, (readCounts.get(file.webkitRelativePath) ?? 0) + 1); return stream(); };
      }
      const start = performance.now();
      const session = await SttvStorageSession.open(files, sttvRules, combinationId), data = await session.initial();
      const openingSeconds = (performance.now() - start) / 1000;
      assert.equal(Object.keys(data.technologies).length, 679);
      const original = JSON.stringify(data.technologies), beforeReads = [...readCounts];
      for (const language of ['ru', 'en'] as const) {
        const layout = sttvLayout(data, language, { ...settings, combination_id: combinationId });
        const positions = new Map(layout.areas.flatMap(area => area.cards.map(card => [card.id, { ...card, area: area.area }])));
        assert.equal(positions.size, 679);
        assert.equal(layout.report.connections.logicalConnections, combinationId === 'reference_default' ? 464 : 463);
        assert.equal(layout.report.connections.bridges, language === 'ru' ? 19 : 24);
        assert.equal(layout.report.connections.crossings, layout.report.connections.bridges);
        assert.ok(layout.report.connections.maxBends <= 4);
        assert.equal(layout.areas.reduce((sum, area) => sum + area.geometry.routes.length, 0), layout.report.connections.logicalConnections);
        for (const area of layout.areas) {
          assert.equal(new Set(area.cards.map(card => `${card.row}:${card.column}`)).size, area.cards.length);
          for (const card of area.cards) {
            const tech = data.technologies[card.id];
            assert.equal(tech.representations.find(r => r.id === data.treeCombination.parameters.variants[card.id])!.area, area.area);
          }
        }
        if (combinationId === 'reference_default') {
          assert.equal(Object.values(data.technologies).filter(t => t.tree.status === 'root').length, 178);
          assert.equal(Object.values(data.technologies).filter(t => t.tree.status === 'resolved').length, 501);
          for (const id of ['tech_encryption_1', 'tech_decryption_1']) {
            assert.equal(positions.get(id)!.area, 'physics');
            assert.equal(data.technologies[id].tree.parent_tech, 'tech_colonial_bureaucracy');
            assert.ok(layout.areas[0].roots.includes(id));
          }
          const lasers = ['tech_lasers_1', 'tech_lasers_2', 'tech_lasers_3', 'tech_lasers_4', 'tech_lasers_5'];
          if (language === 'ru') assert.equal(layout.areas[0].geometry.routes.find(r => r.child === 'tech_energy_torpedoes_2')!.points.length, 2);
          assert.equal(new Set(lasers.map(id => positions.get(id)!.row)).size, 1);
          for (const id of ['tech_arkship_exodus_jump', 'tech_mine_dark_matter',
            ...Object.keys(data.technologies).filter(id => id.startsWith('tech_unique_mutation_'))]) {
            assert.ok(positions.has(id)); assert.equal(positions.get(id)!.column, data.technologies[id].tier);
          }
        }
        reports.push({ openingSeconds, coverage: data.coverage, layout: layout.report,
          statusCounts: Object.values(data.technologies).reduce((counts, tech) => {
            counts[tech.tree.status] = (counts[tech.tree.status] ?? 0) + 1; return counts;
          }, {} as Record<string, number>),
          positions: Object.fromEntries(positions) });
      }
      assert.deepEqual([...readCounts], beforeReads); assert.equal(JSON.stringify(data.technologies), original);
      assert.equal([...readCounts.values()].every(n => n === 1), true);
      assert.equal(data.coverage.verifiedDocuments, 35);
      assert.equal(data.datasets.filter(d => d.state === 'not_loaded').length, data.datasets.length - 1);
    }
    assert.deepEqual(readFileSync(manifestPath), manifestBytes);
    assert.deepEqual(docs.map(doc => statSync(join(directory, doc.path)).mtimeMs), stats);
    mkdirSync('data/frontend-stage7', { recursive: true });
    writeFileSync('data/frontend-stage7/real-layout.json', JSON.stringify(reports, null, 2) + '\n');
    console.log(JSON.stringify(reports.map(({ openingSeconds, layout, statusCounts }) => ({ openingSeconds,
      combination: layout.combination.id, language: layout.language, seconds: layout.seconds,
      areas: layout.areas, crossAreaLinks: layout.hiddenCrossAreaLinks, statusCounts }))));
  });

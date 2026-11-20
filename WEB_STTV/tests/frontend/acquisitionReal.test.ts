import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { SttvStorageSession } from '../../src/frontend/storage/session';
import { sttvLayout } from '../../src/frontend/data/tree/layout';
import settings from '../../config/frontend/tree_layout.json' with { type: 'json' };
import { sttvRealFiles } from './realFiles';
import { sttvRules } from './setHarness';

test('published acquisition profiles open selectively and render the same visible technology set',
  { skip: !process.env.STTV_ACQUISITION_DIR }, async () => {
    const directory = process.env.STTV_ACQUISITION_DIR!;
    const parent = join(directory, '..');
    const publications = JSON.parse(readFileSync(join(parent, 'publication.json'), 'utf8')) as
      { profile: string; combinationId: string; counts: { visible: number } }[];
    const matrix = JSON.parse(readFileSync(join(parent, 'matrix.json'), 'utf8')) as
      { profiles: { profile: string; enabled: string[]; visible: number; hidden: string[] }[] };
    const reports = [];
    for (const publication of publications.filter(p => p.profile !== 'all_reused')) {
      const start = performance.now(), files = await sttvRealFiles(directory);
      let acquisitionReads = 0;
      for (const file of files.filter(f => f.webkitRelativePath.startsWith('set/acquisition/'))) {
        file.stream = () => { acquisitionReads++; throw new Error('Unexpected acquisition read'); };
      }
      const session = await SttvStorageSession.open(files, sttvRules, publication.combinationId);
      const data = await session.initial();
      const expected = matrix.profiles.find(p => p.profile === publication.profile ||
        publication.profile === 'mixed' && p.enabled.length === 2 && p.enabled.includes('dlc002') && p.enabled.includes('dlc036'));
      const openingSeconds = (performance.now() - start) / 1000;
      assert.equal(data.datasets.length, 30);
      assert.equal(data.coverage.verifiedDocuments, 35);
      const visible = Object.values(data.technologies).filter(t => t.tree.visibility?.visible !== false).map(t => t.id);
      assert.equal(visible.length, publication.counts.visible);
      if (expected) {
        assert.equal(visible.length, expected.visible);
        assert.deepEqual(Object.keys(data.technologies).filter(id => !visible.includes(id)).sort(), expected.hidden);
      }
      for (const language of ['ru', 'en'] as const) {
        const layout = sttvLayout(data, language, { ...settings, combination_id: publication.combinationId });
        assert.deepEqual(layout.areas.flatMap(area => area.cards.map(card => card.id)).sort(), [...visible].sort());
        for (const area of layout.areas) {
          assert.equal(new Set(area.cards.map(c => `${c.row}:${c.column}`)).size, area.cards.length);
        }
      }
      const catalog = await session.load(['crisis_paths', 'crisis_levels']);
      assert.equal(catalog.definitions.crisis_paths?.length, 5);
      assert.equal(catalog.definitions.crisis_levels?.length, 25);
      const localized = Object.values(catalog.definitions).flat().filter(d => d!.sourceRef.database.startsWith('crisis_'));
      for (const definition of localized) {
        for (const role of ['nameId', 'descriptionId'] as const) {
          const id = definition!.texts.find(t => t[role])?.[role];
          assert.ok(id);
          for (const language of ['ru', 'en'] as const) {
            assert.equal(catalog.localization[language][id].status,
              definition!.sourceRef.database === 'crisis_levels' ? 'resolved' : 'missing');
          }
        }
      }
      assert.equal(acquisitionReads, 0);
      reports.push({ profile: publication.profile, combination: publication.combinationId,
        openingSeconds, technologies: visible.length, verifiedDocuments: data.coverage.verifiedDocuments,
        crisisPaths: 5, crisisLevels: 25, acquisitionReads });
    }
    writeFileSync(join(parent, 'frontend_acceptance.json'), JSON.stringify(reports, null, 2) + '\n');
    console.log(JSON.stringify(reports));
  });

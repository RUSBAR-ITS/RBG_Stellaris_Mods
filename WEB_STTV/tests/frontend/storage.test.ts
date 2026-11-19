import test from 'node:test';
import assert from 'node:assert/strict';
import { SttvStorageSession } from '../../src/frontend/storage/session';
import { sttvSet, sttvDatabase, sttvTechnology, sttvAssignment, sttvBlock, sttvScalar, sttvLocalization } from './fixtures';
import { sttvFiles } from './manifestFixtures';
import { sttvRules } from './setHarness';

test('opening verifies only technologies, lazy requests coalesce and retain all fragments', async () => {
  const input = sttvSet(sttvDatabase([sttvTechnology('a')]));
  input.find(d => d.database === 'on_actions')!.items = [sttvAssignment('on_day', sttvBlock([])), sttvAssignment('on_day', sttvBlock([]))];
  const files = sttvFiles(input), reads = new Map<string, number>();
  for (const file of files) {
    const stream = file.stream.bind(file);
    file.stream = () => { reads.set(file.webkitRelativePath, (reads.get(file.webkitRelativePath) ?? 0) + 1); return stream(); };
    file.text = async () => { throw new Error('File.text is forbidden'); };
    file.arrayBuffer = async () => { throw new Error('File.arrayBuffer is forbidden'); };
  }
  const session = await SttvStorageSession.open(files, sttvRules), initial = await session.initial();
  assert.equal(initial.coverage.verifiedDocuments, 1);
  assert.equal(initial.datasets.find(d => d.kind === 'events')!.state, 'not_loaded');
  assert.equal(initial.definitions.events, undefined);
  const [a, b] = await Promise.all([session.resolve([{ database: 'on_actions', id: 'on_day' }]),
    session.load(['on_actions'])]);
  assert.equal(a.refs.length, 2); assert.equal(b.definitionIndex.on_actions!.on_day.length, 2);
  assert.equal([...reads.values()].every(value => value === 1), true);
  assert.equal(b.coverage.verifiedDocuments, 2);
});
test('corrupt unused data is deferred, missing declared data fails before any content is loaded', async () => {
  const inputs = sttvSet(sttvDatabase([sttvTechnology('a')])), files = sttvFiles(inputs);
  const eventIndex = files.findIndex(f => f.webkitRelativePath.includes('/events/'));
  const original = files[eventIndex], bytes = await original.text();
  const damaged = new File([bytes.replace('example.txt', 'damaged.txt')], original.name);
  Object.defineProperty(damaged, 'webkitRelativePath', { value: original.webkitRelativePath });
  files[eventIndex] = damaged;
  const session = await SttvStorageSession.open(files, sttvRules);
  const initial = await session.initial(); assert.equal(Object.keys(initial.technologies).length, 1);
  await assert.rejects(session.load(['events']));
  const retained = await session.load(['technologies']);
  assert.deepEqual(retained.technologies, initial.technologies);
  await assert.rejects(SttvStorageSession.open(files.filter((_, i) => i !== eventIndex), sttvRules));
});
test('unlisted extras are ignored and unsafe or conflicting selected paths fail', async () => {
  const files = sttvFiles(sttvSet());
  const extra = new File(['invalid JSON'], 'extra.json');
  Object.defineProperty(extra, 'webkitRelativePath', { value: 'example/extra.json' });
  await SttvStorageSession.open([...files, extra], sttvRules);
  for (const path of ['example/../escape.json', 'example/C:/escape.json', 'example/manifest.json']) {
    const file = new File(['{}'], 'bad.json'); Object.defineProperty(file, 'webkitRelativePath', { value: path });
    await assert.rejects(SttvStorageSession.open([...files, file], sttvRules));
  }
});


test('anonymous roots resolve by NodeRef without an invented object ID', async () => {
  const input = sttvSet(sttvDatabase([sttvTechnology('a')]));
  const endpoints = ['from', 'to'].map(field => ({ ...sttvAssignment(field, sttvScalar('pc_test')),
    enrichments: { localization: sttvLocalization('pc_test') } }));
  input.find(d => d.database === 'terraform')!.items = [sttvAssignment('terraform_link', sttvBlock(endpoints))];
  const session = await SttvStorageSession.open(sttvFiles(input), sttvRules);
  await session.initial();
  const row = session.reader.manifest.datasets.terraform.objects[0];
  const ref = { database: 'terraform' as const, document_id: row.document_id, pointer: row.pointer };
  const result = await session.resolveNodes([ref]);
  assert.deepEqual(result.refs, [ref]);
  assert.equal(result.data.definitions.terraform!.length, 1);
  assert.equal(result.data.coverage.documents.find(d => d.document_id === row.document_id)!.state, 'loaded');
  assert.throws(() => session.resolveNodes([{ ...ref, pointer: '/items/999' }]));
});

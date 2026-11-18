import test from 'node:test';
import assert from 'node:assert/strict';
import { SttvJsonStream, sttvReadJson } from '../../src/frontend/data/jsonStream';
import { SttvSetAdapter } from '../../src/frontend/data/setAdapter';
import { sttvRules, sttvAdaptSet } from './setHarness';
import { sttvSet, sttvSetFiles, sttvTechnology, sttvDatabase, sttvScalar } from './fixtures';
import type { SttvDatabase } from '../../src/frontend/data/syntax';

test('streamed documents produce the same catalog with original addresses and late references', async () => {
  const db = sttvDatabase([sttvTechnology('child', 1, 'physics', [sttvScalar('parent')])]);
  db.documents.push({ source: { file: 'common/technology/second.txt', root: 'STELLARIS_ROOT' },
    items: [sttvTechnology('parent')] });
  const inputs = sttvSet(db).reverse(), files = sttvSetFiles(inputs);
  const adapter = new SttvSetAdapter(files, sttvRules);
  for (const [index, input] of inputs.entries()) {
    const file = new Blob([JSON.stringify(input)]);
    const { metadata, documentCount } = await sttvReadJson(file);
    assert.equal(metadata.documents.length, 0);
    adapter.begin(metadata, index);
    adapter.metadata.datasets.at(-1)!.documentCount = documentCount;
    await sttvReadJson(file, (document, offset) => adapter.document({ ...metadata, documents: [document] }, index, offset));
  }
  assert.deepEqual(adapter.finish(), sttvAdaptSet(inputs, files));
});
test('every character boundary preserves escapes, Unicode, numbers and metadata ordering', () => {
  const input = { documents: [{ items: [], metadata: { ignored: '\\"\nЖ😀' }, source: { file: 'Ж😀\\"\n.txt', root: 'STELLARIS_ROOT' } }],
    format: 'sttv.parse_database', format_version: 6, dataset: { kind: 'events', set_id: 'a'.repeat(64) }, ignored: -1.25e-3 };
  const text = JSON.stringify(input);
  for (let boundary = 1; boundary < text.length; boundary++) {
    const docs: SttvDatabase['documents'] = [], parser = new SttvJsonStream(doc => docs.push(doc));
    parser.tokens.feed(text.slice(0, boundary)); parser.tokens.feed(text.slice(boundary));
    assert.equal(parser.finish().format_version, 6);
    assert.equal(docs[0].source.file, input.documents[0].source.file);
    assert.equal('metadata' in docs[0], false);
  }
});
test('stream rejects malformed and unfinished JSON even in discarded metadata', () => {
  for (const text of ['{"documents":[],}', '{"documents":[}', '{"documents":[] "x":1}',
    '{"documents":[],"x":01}', '{"documents":[],"x":"\\uXX00"}',
    '{"documents":[],"x":"unfinished', '{"documents":[],"x":true', '{"documents":[]}null']) {
    const parser = new SttvJsonStream();
    assert.throws(() => { for (const char of text) parser.tokens.feed(char); parser.finish(); }, SyntaxError, text);
  }
});
test('UTF-8 multibyte sequences split between byte chunks decode correctly', async () => {
  const bytes = new TextEncoder().encode(JSON.stringify({ documents: [], dataset: { kind: 'Событие😀' } }));
  const stream = new ReadableStream({ start(controller) {
    for (const byte of bytes) controller.enqueue(new Uint8Array([byte])); controller.close();
  } });
  const { metadata } = await sttvReadJson({ stream: () => stream } as Blob);
  assert.equal(metadata.dataset!.kind, 'Событие😀');
});

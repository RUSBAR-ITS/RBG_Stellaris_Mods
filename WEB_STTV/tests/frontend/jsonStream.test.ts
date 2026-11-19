import test from 'node:test';
import assert from 'node:assert/strict';
import { SttvJsonStream, sttvReadJson } from '../../src/frontend/data/jsonStream';
import { SttvStorageSession } from '../../src/frontend/storage/session';
import { sttvRules, sttvAdaptSet } from './setHarness';
import { sttvSet, sttvTechnology, sttvDatabase, sttvScalar } from './fixtures';
import { sttvFiles, sttvHash } from './manifestFixtures';
import type { SttvNode } from '../../src/frontend/data/syntax';
import { sttvDatabaseKinds } from '../../src/frontend/data/registry';

test('streamed items produce the same catalogs and preserve late references', async () => {
  const inputs = sttvSet(sttvDatabase([sttvTechnology('child', 1, 'physics', [sttvScalar('parent')]), sttvTechnology('parent')]));
  const session = await SttvStorageSession.open(sttvFiles(inputs).reverse(), sttvRules);
  const streamed = await session.load(sttvDatabaseKinds), direct = sttvAdaptSet(inputs);
  assert.deepEqual(streamed.technologies, direct.technologies);
  assert.deepEqual(JSON.parse(JSON.stringify(streamed.localization)), JSON.parse(JSON.stringify(direct.localization)));
  assert.equal(streamed.coverage.verifiedDocuments, 15);
});
test('character boundaries preserve Unicode and discard only unused payload fields', () => {
  const input = { ...sttvDatabase([sttvTechnology('example')]), metadata: { ignored: '\\"\n\u0416\ud83d\ude00' } };
  input.source.file = 'common/technology/\u0416\ud83d\ude00.txt';
  const text = JSON.stringify(input);
  for (let boundary = 1; boundary < text.length; boundary++) {
    const items: SttvNode[] = [], parser = new SttvJsonStream(item => items.push(item));
    parser.tokens.feed(text.slice(0, boundary)); parser.tokens.feed(text.slice(boundary));
    const header = parser.finish();
    assert.equal(header.source.file, input.source.file);
    assert.equal('metadata' in header, false);
    assert.deepEqual(JSON.parse(JSON.stringify(items)), input.items);
  }
});
test('malformed and duplicate JSON fails even inside discarded metadata', () => {
  for (const text of ['{"items":[],}', '{"items":[}', '{"items":[] "x":1}',
    '{"items":[],"x":01}', '{"items":[],"x":"\\uXX00"}', '{"items":[],"x":"unfinished',
    '{"items":[],"x":true', '{"items":[]}null', '{"items":[],"x":{"a":1,"a":2}}']) {
    const parser = new SttvJsonStream();
    assert.throws(() => { for (const char of text) parser.tokens.feed(char); parser.finish(); }, SyntaxError, text);
  }
});
test('incremental UTF-8 decoding and hashing share the same single byte pass', async () => {
  const text = JSON.stringify({ items: [], database: '\u0421\u043e\u0431\u044b\u0442\u0438\u0435\ud83d\ude00' });
  const bytes = new TextEncoder().encode(text);
  let reads = 0;
  const blob = { stream: () => { reads++; return new ReadableStream({ start(controller) {
    for (const byte of bytes) controller.enqueue(new Uint8Array([byte])); controller.close();
  } }); } } as Blob;
  const parsed = await sttvReadJson(blob);
  assert.equal(parsed.metadata.database, JSON.parse(text).database);
  assert.equal(parsed.hash, sttvHash(text)); assert.equal(parsed.bytes, bytes.length); assert.equal(reads, 1);
});

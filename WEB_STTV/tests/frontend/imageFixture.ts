import { createHash } from 'node:crypto';
import { sttvDatabase, sttvTechnology, sttvSet } from './fixtures';
import { sttvBundle } from './manifestFixtures';

export const sttvPng = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFUlEQVR4nGMUSdnSwMDAwMAEIkAYABlWAbActfn+AAAAAElFTkSuQmCC', 'base64');

export function sttvImageFixture(bytes = sttvPng) {
  const id = createHash('sha256').update(bytes).digest('hex');
  const nodes = ['a', 'b', 'c'].map(name => {
    const node = sttvTechnology(name);
    Object.assign(node.enrichments, { presentation: { format_version: 1, icon_asset_id: id } });
    return node;
  });
  const bundle = sttvBundle(sttvSet(sttvDatabase(nodes)));
  const presentation = bundle.manifest.presentation!;
  presentation.files[id] = { path: `assets/${id}.png`, mime_type: 'image/png', file_hash: id,
    byte_size: bytes.length, width: 2, height: 2 };
  bundle.entries.find(entry => entry.path === 'manifest.json')!.content = JSON.stringify(bundle.manifest);
  return { id, presentation, entries: [...bundle.entries, { path: `assets/${id}.png`, content: bytes }] };
}

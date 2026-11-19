import { readFileSync, openAsBlob } from 'node:fs';
import { join, basename } from 'node:path';
import type { SttvManifest } from '../../src/frontend/storage/model';

export async function sttvRealFiles(directory: string) {
  const manifest = JSON.parse(readFileSync(join(directory, 'manifest.json'), 'utf8')) as SttvManifest;
  const paths = ['manifest.json', ...Object.values(manifest.datasets).flatMap(d => d.documents.map(row => row.path))];
  return Promise.all(paths.map(async path => {
    const file = await openAsBlob(join(directory, path));
    Object.defineProperties(file, { name: { value: basename(path) }, webkitRelativePath: { value: 'set/' + path } });
    return file as File;
  }));
}

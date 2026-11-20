import type { SttvManifest } from './model';
import { sttvSetError } from '../data/setMetadata';

export interface SttvBytes { size: number; stream(): ReadableStream<Uint8Array<ArrayBuffer>> }
export type SttvRemoteBytes = (path: string) => Promise<SttvBytes>;

export async function sttvBytes(files: Map<string, File>, path: string, remote?: SttvRemoteBytes): Promise<SttvBytes> {
  const file = files.get(path);
  if (file) return file;
  if (remote) return remote(path);
  return sttvSetError('Declared file is not available.', { path });
}

export function sttvSnapshotFiles(manifest: SttvManifest, files: Map<string, File>) {
  const paths = new Set([...Object.values(manifest.datasets).flatMap(d => d.documents.map(r => r.path)),
    ...Object.values(manifest.presentation?.files ?? {}).map(r => r.path)]);
  return new Map([...files].filter(([path]) => paths.has(path)));
}

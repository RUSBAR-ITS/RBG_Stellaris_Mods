import { sha256 } from '@noble/hashes/sha2.js';
import { bytesToHex } from '@noble/hashes/utils.js';
import type { SttvStoredString } from '../localization/model';
import type { SttvCatalog } from '../data/model';
import { sttvRepresentation } from '../data/tree/comparison';
import { sttvDiagnostic, type SttvDiagnostic } from '../workers/diagnostics';
import { sttvSetError } from '../data/setMetadata';
import { sttvBytes, type SttvRemoteBytes } from './bytes';

export interface SttvAssetDescriptor {
  path: string; mime_type: 'image/png'; file_hash: string; byte_size: number; width: number; height: number;
}
export interface SttvPresentation {
  format_version: 1;
  revision: string;
  files: Record<string, SttvAssetDescriptor>;
  research_icons: Record<string, string | null>;
  categories: Record<string, { ru: SttvStoredString; en: SttvStoredString }>;
  dlc_icons?: Record<string, string | null>;
}
export interface SttvCachedImage { blob: Blob | null; diagnostic?: SttvDiagnostic }

export function sttvCheckPresentation(value: SttvPresentation, relative: (path: string) => string, paths: Set<string>) {
  if (value?.format_version !== 1 || !value.files || !value.categories || !value.research_icons
    || !/^[a-f0-9]{64}$/.test(value.revision)) sttvSetError('Invalid resource preparation contract.');
  for (const [id, row] of Object.entries(value.files)) {
    if (!/^[a-f0-9]{64}$/.test(id) || id !== row.file_hash || row.mime_type !== 'image/png'
      || [row.byte_size, row.width, row.height].some(n => !Number.isSafeInteger(n) || n <= 0)) sttvSetError('Invalid resource descriptor.', { id });
    const path = relative(row.path).toLowerCase();
    if (paths.has(path)) sttvSetError('Conflicting resource path.', { path });
    paths.add(path);
  }
  for (const area of ['physics', 'society', 'engineering']) {
    const id = value.research_icons[area];
    if (id !== null && !value.files[id]) sttvSetError('Research icon is not declared.', { area });
  }
  for (const id of Object.values(value.dlc_icons ?? {})) {
    if (id !== null && !value.files[id]) sttvSetError('DLC image is not declared.', { id });
  }
  for (const [id, languages] of Object.entries(value.categories)) for (const language of ['ru', 'en'] as const) {
    if (!languages?.[language] || typeof languages[language].requested_key !== 'string'
      || !(languages[language].text === null || typeof languages[language].text === 'string')) sttvSetError('Invalid category name.', { id, language });
  }
}

export async function sttvLoadAssets(data: SttvCatalog, presentation: SttvPresentation,
  files: Map<string, File>, cache: Map<string, SttvCachedImage>, remote?: SttvRemoteBytes) {
  const ids = new Set<string>();
  for (const tech of Object.values(data.technologies)) {
    if (tech.tree.visibility?.visible === false) continue;
    const rep = sttvRepresentation(tech, data.treeCombination.parameters.variants);
    if (rep.iconAssetId) ids.add(rep.iconAssetId);
    else data.diagnostics.push(sttvDiagnostic('image_unavailable', 'reading', { technology: tech.id, representation: rep.id }));
    if (tech.cost !== null) {
      const resource = presentation.research_icons[rep.area];
      if (resource) ids.add(resource);
      else data.diagnostics.push(sttvDiagnostic('image_unavailable', 'reading', { technology: tech.id, resource: rep.area }));
    }
  }
  for (const entry of data.definitions.dlcs ?? []) {
    const id = presentation.dlc_icons?.[entry.id!];
    if (id) ids.add(id);
  }
  for (const id of ids) {
    if (cache.has(id)) continue;
    const row = presentation.files[id];
    if (!row) sttvSetError('Image reference is missing from the resource registry.', { id });
    try {
      const file = await sttvBytes(files, row.path, remote);
      if (!file || file.size !== row.byte_size) throw new Error('Resource is missing or has the wrong size.');
      const bytes = new Uint8Array(await new Response(file.stream()).arrayBuffer());
      if (bytesToHex(sha256(bytes)) !== row.file_hash) throw new Error('Resource hash mismatch.');
      const view = new DataView(bytes.buffer);
      if (bytes.length < 24 || view.getUint32(0) !== 0x89504e47 || view.getUint32(4) !== 0x0d0a1a0a
        || view.getUint32(16) !== row.width || view.getUint32(20) !== row.height) throw new Error('Invalid PNG header/dimensions.');
      cache.set(id, { blob: new Blob([bytes], { type: row.mime_type }) });
    } catch (error) {
      cache.set(id, { blob: null, diagnostic: sttvDiagnostic('image_unavailable', 'reading', { id, path: row.path, reason: String(error) }) });
    }
  }
  data.presentation = presentation;
  data.images = Object.fromEntries([...ids].map(id => [id, cache.get(id)!.blob]));
  data.diagnostics.push(...[...ids].flatMap(id => cache.get(id)!.diagnostic ? [cache.get(id)!.diagnostic!] : []));
  for (const [id, languages] of Object.entries(presentation.categories)) {
    for (const language of ['ru', 'en'] as const) {
      const value = languages[language], existing = data.localization[language][id];
      if (existing?.text && value.text && existing.text !== value.text) sttvSetError('Conflicting category localization.', { id, language });
      if (!existing) data.localization[language][id] = { text: value.text ?? id,
        status: 'resolved', origins: [] };
      if (value.text === null) data.diagnostics.push(sttvDiagnostic('missing_localization', 'preparing', { id, language, category: true }));
    }
  }
  return data;
}

import { existsSync, realpathSync } from 'node:fs';
import { basename, dirname, isAbsolute, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import globals from './global_variables.json' with { type: 'json' };

function physical(path: string): string {
  if (existsSync(path)) return realpathSync(path);
  const parent = dirname(path);
  if (parent === path) throw new Error('Workspace volume is unavailable');
  return resolve(physical(parent), basename(path));
}

const product = realpathSync(dirname(fileURLToPath(import.meta.url)));
const repository = dirname(product);
const workspace = physical(resolve(product, globals.WORK_DIR));

function inside(parent: string, child: string) {
  const path = relative(parent, child);
  return path !== '' && path !== '..' && !path.startsWith('..' + sep) && !isAbsolute(path);
}

export function sttvWorkPath(name: string) {
  const result = physical(resolve(workspace, name));
  if (!inside(repository, workspace) || workspace === product || !inside(workspace, result)) {
    throw new Error('Unsafe frontend workspace or output path');
  }
  const git = resolve(repository, '.git');
  if (workspace === git || inside(git, workspace)) throw new Error('Protected repository directory');
  for (const path of ['src', 'config', 'Docs', 'schemas', 'node_modules', 'tests', 'language']) {
    const protectedPath = resolve(product, path);
    if (result === protectedPath || inside(protectedPath, result)) throw new Error('Protected frontend output path');
  }
  return result;
}

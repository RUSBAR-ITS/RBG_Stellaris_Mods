import { SttvJsonTokens, type SttvJsonToken } from './jsonTokens';
import type { SttvDatabase } from './syntax';
import { sttvSetError } from './setMetadata';

type SttvPath = (string | number)[];
interface SttvFrame {
  path: SttvPath; array: boolean; state: 'first' | 'key' | 'colon' | 'value' | 'comma';
  index: number; key: string; keep: boolean; value: Record<string, unknown> | unknown[];
}
const sttvNodeFields = new Set(['kind', 'text', 'key', 'operator', 'value', 'body', 'items', 'enrichments']);

/** Validate JSON while retaining only root metadata or one consumed document. */
export class SttvJsonStream {
  private stack: SttvFrame[] = [];
  private complete = false;
  private result: unknown;
  private documentArray = false;
  documentCount = 0;
  readonly tokens = new SttvJsonTokens(token => this.accept(token));
  constructor(private document?: (value: SttvDatabase['documents'][number], index: number) => void) {}

  private path(): SttvPath {
    const parent = this.stack.at(-1);
    return parent ? [...parent.path, parent.array ? parent.index : parent.key] : [];
  }
  private retain(path: SttvPath): boolean {
    if (!path.length) return true;
    if (path[0] !== 'documents') return path.length === 1
      ? ['format', 'format_version', 'dataset'].includes(String(path[0])) : this.stack.at(-1)!.keep;
    if (path.length === 1 || !this.document) return false;
    if (path.length === 2) return true;
    if (!this.stack.at(-1)!.keep) return false;
    if (path.length === 3) return ['source', 'items'].includes(String(path[2]));
    if (path[2] === 'source' || path.includes('enrichments')) return true;
    return typeof path.at(-1) === 'number' || sttvNodeFields.has(String(path.at(-1)));
  }
  private place(value: unknown, path: SttvPath, keep: boolean) {
    if (path.length === 2 && path[0] === 'documents') {
      this.documentCount++;
      this.document?.(value as SttvDatabase['documents'][number], Number(path[1]));
    }
    const parent = this.stack.at(-1);
    if (!parent) { this.result = value; this.complete = true; return; }
    if (keep && parent.keep) {
      if (parent.array) (parent.value as unknown[]).push(value);
      else (parent.value as Record<string, unknown>)[parent.key] = value;
    }
    parent.index++; parent.state = 'comma';
  }
  private accept(token: SttvJsonToken) {
    const parent = this.stack.at(-1), punctuation = token.kind === 'punctuation' ? token.value : null;
    if (this.complete) throw new SyntaxError('Data after the JSON root.');
    if (parent) {
      if (parent.state === 'comma') {
        if (punctuation === ',') { parent.state = parent.array ? 'value' : 'key'; return; }
        if (punctuation !== (parent.array ? ']' : '}')) throw new SyntaxError('Expected a comma or container end.');
      }
      if (punctuation === ']' || punctuation === '}') {
        if (punctuation !== (parent.array ? ']' : '}') || !['first', 'comma'].includes(parent.state)) {
          throw new SyntaxError('Unexpected JSON container end.');
        }
        this.stack.pop(); this.place(parent.value, parent.path, parent.keep); return;
      }
      if (!parent.array && (parent.state === 'first' || parent.state === 'key')) {
        if (token.kind !== 'string') throw new SyntaxError('Expected an object key.');
        parent.key = token.value as string; parent.state = 'colon'; return;
      }
      if (parent.state === 'colon') {
        if (punctuation !== ':') throw new SyntaxError('Expected a colon.');
        parent.state = 'value'; return;
      }
      if (!['first', 'value'].includes(parent.state)) throw new SyntaxError('Unexpected JSON value.');
    }
    const path = this.path(), keep = this.retain(path);
    if (path.length === 1 && path[0] === 'documents') {
      if (punctuation !== '[') sttvSetError('Documents must be an array.');
      if (this.documentArray) throw new SyntaxError('Repeated documents property.');
      this.documentArray = true;
    }
    if (punctuation === '{' || punctuation === '[') {
      this.stack.push({ path, keep, array: punctuation === '[', state: 'first', index: 0, key: '',
        value: punctuation === '[' ? [] : Object.create(null) });
    } else if (token.kind !== 'punctuation') this.place(token.value, path, keep);
    else throw new SyntaxError('Expected a JSON value.');
  }
  finish() {
    this.tokens.feed('', true);
    if (!this.complete || this.stack.length) throw new SyntaxError('Incomplete JSON document.');
    return { ...(this.result as SttvDatabase), ...(this.documentArray ? { documents: [] } : {}) };
  }
}

export async function sttvReadJson(file: Blob, document?: ConstructorParameters<typeof SttvJsonStream>[0]) {
  const parser = new SttvJsonStream(document);
  const reader = file.stream().pipeThrough(new TextDecoderStream('utf-8', { fatal: true })).getReader();
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      parser.tokens.feed(value);
    }
    return { metadata: parser.finish(), documentCount: parser.documentCount };
  } finally { await reader.cancel(); reader.releaseLock(); }
}

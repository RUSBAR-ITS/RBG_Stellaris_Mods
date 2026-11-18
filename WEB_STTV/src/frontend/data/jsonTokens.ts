export type SttvJsonToken = { kind: 'punctuation' | 'string' | 'value'; value: unknown };

/** Incremental JSON tokens; partial escapes and UTF-16 units stay inside a token. */
export class SttvJsonTokens {
  private mode: 'string' | 'atom' | null = null;
  private parts: string[] = [];
  private escaped = false;
  constructor(private emit: (token: SttvJsonToken) => void) {}

  feed(text: string, final = false) {
    let i = 0;
    while (i < text.length) {
      if (this.mode === 'string') {
        const start = i;
        let closed = false;
        while (i < text.length) {
          const character = text[i++];
          if (character.charCodeAt(0) < 32) throw new SyntaxError('Control character inside JSON string.');
          if (this.escaped) this.escaped = false;
          else if (character === '\\') this.escaped = true;
          else if (character === '"') { closed = true; break; }
        }
        this.parts.push(text.slice(start, i));
        if (closed) this.flush('string');
        continue;
      }
      if (this.mode === 'atom') {
        const start = i;
        while (i < text.length && !/[ \t\r\n{}\[\]:,"]/.test(text[i])) i++;
        this.parts.push(text.slice(start, i));
        if (i < text.length) this.flush('value');
        continue;
      }
      const whitespace = /[ \t\r\n]+/y;
      whitespace.lastIndex = i;
      if (whitespace.test(text)) { i = whitespace.lastIndex; continue; }
      const character = text[i++];
      if ('{}[]:,'.includes(character)) this.emit({ kind: 'punctuation', value: character });
      else if (character === '"') { this.mode = 'string'; this.parts = ['"']; }
      else { this.mode = 'atom'; this.parts = [character]; }
    }
    if (final) {
      if (this.mode === 'string') throw new SyntaxError('Unterminated JSON string.');
      if (this.mode === 'atom') this.flush('value');
    }
  }
  private flush(kind: 'string' | 'value') {
    const raw = this.parts.join('');
    const value: unknown = JSON.parse(raw);
    if (kind === 'value' && !/^(?:true|false|null|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)$/.test(raw)) {
      throw new SyntaxError('Invalid JSON primitive.');
    }
    this.mode = null; this.parts = []; this.escaped = false;
    this.emit({ kind, value });
  }
}

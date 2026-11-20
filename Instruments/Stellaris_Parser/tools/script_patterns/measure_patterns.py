"""Aggregate complete lexical and structural observations, retaining evidence."""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re

from structure_probe import Probe, ProbeError, lex, value_kind

DOCUMENTS = {'common/HOW_TO_MAKE_NEW_SHIPS.txt', 'common/edicts/99_README_EDICTS.txt'}


class Measures:
    def __init__(self):
        self.counts, self.operators, self.keys = Counter(), Counter(), Counter()
        self.files, self.examples = defaultdict(set), defaultdict(list)
        self.block_shapes, self.tags = Counter(), Counter()
        self.depth, self.root_bare = 0, []
        self.parameter_names, self.math_symbols = Counter(), Counter()
        self.mixed, self.safe_keys, self.colon_prefixes = [], Counter(), Counter()
        self.unusual_atoms, self.macro_calls = Counter(), Counter()

    def add(self, kind, path, token, value=None):
        self.counts[kind] += 1
        self.files[kind].add(path)
        if len(self.examples[kind]) < 8:
            self.examples[kind].append({'file': path, 'line': token.line,
                                       'value': (value or token.text)[:400]})

    def lexical(self, tokens, path):
        for t in tokens:
            self.add('lex_' + t.kind, path, t)
            if t.kind in ('string', 'atom', 'math'):
                for m in re.finditer(r'\$([A-Za-z_][A-Za-z_0-9]*)(?:\|([^$]*))?\$', t.text):
                    self.parameter_names[m[1]] += 1
                    self.add('parameter_default' if m[2] is not None else 'parameter', path, t, m[0])
            if t.kind == 'string':
                for kind, match in [('multiline_string', '\n' in t.text),
                                    ('escaped_quote', '\\"' in t.text),
                                    ('string_hash', '#' in t.text),
                                    ('string_braces', '{' in t.text),
                                    ('string_brackets', '[' in t.text)]:
                    if match:
                        self.add(kind, path, t)
            if t.kind == 'math':
                self.math_symbols.update(re.findall(r'[+*/^%|()-]', t.text))
            if t.kind == 'atom' and not re.fullmatch(r'[\w@.:/$|+\\-]+', t.text):
                self.add('unusual_atom', path, t)
                self.unusual_atoms[t.text] += 1

    def walk(self, nodes, path, depth=0, parent='<root>'):
        self.depth = max(self.depth, depth)
        shape = '+'.join(sorted(set(n.form for n in nodes))) or 'empty'
        self.block_shapes[shape] += 1
        if 'bare_scalar' in shape and '+' in shape:
            self.mixed.append({'file': path, 'line': nodes[0].start.line, 'parent': parent,
                               'bare': [n.value.text for n in nodes if n.form == 'bare_scalar']})
        names = Counter(n.key.text for n in nodes if n.key is not None)
        for key, count in names.items():
            if count > 1:
                self.add('duplicate_key_in_container', path, nodes[0].start, f'{key}: {count}')
        for n in nodes:
            self.add(n.form, path, n.start)
            if n.key:
                self.keys[n.key.text] += 1
                self.operators[n.operator] += 1
                if n.key.kind == 'string':
                    self.add('quoted_key', path, n.key)
                if '?' in n.key.text:
                    self.add('question_mark_key', path, n.key)
                    self.safe_keys[n.key.text] += 1
                for label, match in [('at_definition', n.key.text.startswith('@')),
                                     ('numeric_key', bool(re.fullmatch(r'\d+', n.key.text))),
                                     ('colon_key', ':' in n.key.text),
                                     ('dotted_key', '.' in n.key.text),
                                     ('parameter_key', '$' in n.key.text)]:
                    if match:
                        self.add(label, path, n.key)
            if n.tag:
                self.tags[n.tag.text] += 1
            if n.value:
                self.add('value_' + value_kind(n.value), path, n.value)
                if n.value.kind == 'atom' and ':' in n.value.text:
                    self.colon_prefixes[n.value.text.split(':', 1)[0]] += 1
                if n.value.kind == 'atom' and '|' in n.value.text and ':' in n.value.text:
                    self.add('pipe_arguments', path, n.value)
            if n.key and n.key.text == 'inline_script':
                self.add('inline_' + n.form, path, n.start)
            if n.children is not None:
                if not n.children:
                    self.add('empty_block', path, n.start)
                self.walk(n.children, path, depth + 1, n.key.text if n.key else n.form)
            if depth == 0 and n.form == 'bare_scalar':
                self.root_bare.append({'file': path, 'line': n.start.line, 'value': n.start.text})


def paths():
    parser = argparse.ArgumentParser(description="Measure and verify common/ and events/ script structure.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root, output = args.source.resolve(), args.output.resolve()
    if not root.is_dir() or output.is_relative_to(root):
        parser.error("Supply an existing source directory and a separate output directory")
    output.mkdir(parents=True, exist_ok=True)
    return root, output


def inventory(root):
    files, directories = [], defaultdict(Counter)
    for folder in ("common", "events"):
        for path in sorted((root / folder).rglob("*")):
            if not path.is_file():
                continue
            raw = path.read_bytes()
            extension = path.suffix.lower() or "<none>"
            directories[path.parent.relative_to(root).as_posix()][extension] += 1
            item = {"file": path.relative_to(root).as_posix(), "bytes": len(raw),
                    "extension": extension, "sha256": sha256(raw).hexdigest()}
            if extension == ".txt":
                item["lines"] = len(raw.splitlines())
                item["encoding"] = "utf-8-sig" if raw.startswith(bytes.fromhex("efbbbf")) else "utf-8"
            files.append(item)
    if not files:
        raise ValueError(f"No files under common/ or events/ in {root}")
    return {"root": str(root), "files": files, "directories": directories}


def main():
    root, output = paths()
    base = inventory(root)
    (output / 'baseline_audit.json').write_text(json.dumps(base, indent=2) + '\n', encoding='utf-8')
    measures = Measures()
    failures, results, lexical_failures = [], [], []
    for item in base['files']:
        if item['extension'] != '.txt':
            continue
        path = item['file']
        raw = (root / path).read_bytes()
        assert sha256(raw).hexdigest() == item['sha256'], path
        source = raw.decode('utf-8-sig')
        result = {'file': path}
        if path in DOCUMENTS:
            result['status'] = 'prose_document_reviewed_separately'
            results.append(result)
            continue
        tokens = list(lex(source))
        assert ''.join(t.text for t in tokens) == source, path
        measures.lexical(tokens, path)
        for t in tokens:
            if t.kind == 'unknown':
                lexical_failures.append({'file': path, 'line': t.line, 'value': t.text})
        try:
            nodes = Probe(tokens).sequence()
            measures.walk(nodes, path)
            result.update(status='structurally_scanned', root_forms=dict(Counter(n.form for n in nodes)))
            if not nodes:
                result['status'] = 'comments_or_whitespace_only'
        except ProbeError as exc:
            result['status'] = 'unresolved'
            failures.append({'file': path, 'line': exc.token.line, 'message': str(exc)})
        results.append(result)
    data = {'files': results, 'failures': failures, 'lexical_failures': lexical_failures,
            'counts': measures.counts, 'file_counts': {k: len(v) for k,v in measures.files.items()},
            'examples': measures.examples, 'operators': measures.operators,
            'keys': measures.keys, 'block_shapes': measures.block_shapes, 'tags': measures.tags,
            'max_depth': measures.depth, 'root_bare': measures.root_bare,
            'parameter_names': measures.parameter_names, 'math_symbols': measures.math_symbols}
    data.update(mixed=measures.mixed, safe_keys=measures.safe_keys,
                colon_prefixes=measures.colon_prefixes, unusual_atoms=measures.unusual_atoms)
    (output / 'pattern_audit.json').write_text(json.dumps(data, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'statuses': Counter(x['status'] for x in results),
                      'failures': failures, 'lexical_failures': lexical_failures,
                      'counts': measures.counts, 'operators': measures.operators}, indent=2))


if __name__ == '__main__':
    main()

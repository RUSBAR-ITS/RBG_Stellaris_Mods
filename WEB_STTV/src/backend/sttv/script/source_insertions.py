"""Token-scoped separator repairs with original source coordinates."""

from .lexer import Lexer
from .nodes import Source
from sttv.common.errors import BuildError


class InsertedSource(Source):
    def __init__(self, original, offset, value):
        super().__init__(original.text[:offset] + value + original.text[offset:],
                         original.file, original.root, original.call_id)
        self.original, self.offset, self.width = original, offset, len(value)

    def position(self, value):
        return value if value <= self.offset else max(self.offset, value - self.width)

    def origin(self, start, end):
        return self.original.origin(self.position(start), self.position(end))

    def original_text(self, start, end):
        return self.original.original_text(self.position(start), self.position(end))


def repair(source, syntax, context):
    exceptions = context.exceptions
    if exceptions is None or source.root != 'STELLARIS_ROOT':
        return source
    context.root_source = source.origin(0, 0)
    rules = exceptions.candidates(context, 'missing_assignment_separator')
    for rule in rules:
        match = rule['match']
        tokens = [t for t in Lexer(source, syntax).tokens() if t.kind not in ('space', 'comment', 'bom')]
        stack, matches = [], []
        for i, token in enumerate(tokens):
            if token.kind == 'open':
                name = tokens[i - 2].raw if i >= 2 and tokens[i - 1].raw == '=' else None
                stack.append(name)
            elif token.kind == 'close':
                if stack:
                    stack.pop()
            elif (stack == match['containers'] and token.kind == 'atom' and token.raw == match['field']
                  and (i == 0 or tokens[i - 1].kind != 'operator')
                  and i + 1 < len(tokens) and tokens[i + 1].kind == 'string'
                  and tokens[i + 1].raw == match['value']):
                matches.append((token, tokens[i + 1]))
        if len(matches) > 1:
            raise BuildError('source_exception_conflict', f"Ambiguous repair: {rule['id']}")
        if matches:
            key, value = matches[0]
            before = source.text[key.span.start:value.span.end]
            exceptions.log(context, rule, source, key.span.start, before,
                           key.raw + ' = ' + value.raw, exceptions.config_file)
            source = InsertedSource(source, key.span.end, rule['action']['insert'])
    return source

"""Corpus-only structural probe; no command registry and no game execution."""

from dataclasses import dataclass
import re

LEXEMES = re.compile(
    r'(?P<space>\s+)|(?P<comment>\#[^\r\n]*)'
    r'|(?P<string>"(?:[^"\\]|\\[\s\S])*")'
    r'|(?P<math>@\\?\[[^\]]*\])'
    r'|(?P<conditional>\[\[!?[A-Za-z_][A-Za-z_0-9]*\])'
    r'|(?P<operator>\?=|!=|<=|>=|=|<|>)'
    r'|(?P<punctuation>[{}\[\]])'
    r'|(?P<atom>[^\s#"{}\[\]=<>!]+)'
    r'|(?P<unknown>[\s\S])'
)


@dataclass
class Token:
    kind: str
    text: str
    line: int
    offset: int


@dataclass
class Node:
    form: str
    start: Token
    key: Token | None = None
    operator: str | None = None
    value: Token | None = None
    tag: Token | None = None
    children: list | None = None


def lex(source):
    line = 1
    for match in LEXEMES.finditer(source):
        token = Token(match.lastgroup, match.group(), line, match.start())
        yield token
        line += token.text.count('\n')


class ProbeError(Exception):
    def __init__(self, message, token):
        self.message, self.token = message, token
        super().__init__(f'{message} at line {token.line}: {token.text[:80]}')


class Probe:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.kind not in ('space', 'comment')]
        self.index = 0

    def peek(self):
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def take(self):
        token = self.peek()
        if token is None:
            raise ProbeError('Unexpected end of input', self.tokens[-1])
        self.index += 1
        return token

    def sequence(self, end=None):
        nodes = []
        while self.peek() is not None:
            token = self.take()
            if token.kind == 'punctuation' and token.text == end:
                return nodes
            if token.kind == 'conditional':
                nodes.append(Node('conditional', token, children=self.sequence(']')))
                continue
            if token.kind == 'punctuation' and token.text == '{':
                nodes.append(Node('anonymous_block', token, children=self.sequence('}')))
                continue
            if token.kind not in ('atom', 'string', 'math'):
                raise ProbeError('Expected entry', token)
            following = self.peek()
            if following and following.kind == 'operator':
                operator = self.take().text
                value = self.take()
                if value.text == '{' and value.kind == 'punctuation':
                    node = Node('key_block', token, token, operator, children=self.sequence('}'))
                elif value.kind in ('atom', 'string', 'math'):
                    if self.peek() and self.peek().text == '{':
                        self.take()
                        node = Node('tagged_value', token, token, operator, tag=value,
                                    children=self.sequence('}'))
                    else:
                        node = Node('key_scalar', token, token, operator, value=value)
                else:
                    raise ProbeError('Expected value', value)
                nodes.append(node)
            elif following and following.text == '{':
                self.take()
                nodes.append(Node('labelled_block', token, tag=token, children=self.sequence('}')))
            else:
                nodes.append(Node('bare_scalar', token, value=token))
        if end is not None:
            raise ProbeError(f'Missing closing {end}', self.tokens[-1])
        return nodes


def value_kind(token):
    if token.kind == 'string':
        return 'quoted'
    if token.kind == 'math':
        return 'deferred_math' if token.text.startswith('@\\') else 'math'
    value = token.text
    if value in ('yes', 'no'):
        return 'yes_no'
    if re.fullmatch(r'[+-]?\d+', value):
        return 'integer'
    if re.fullmatch(r'[+-]?(?:\d+\.\d*|\.\d+)', value):
        return 'decimal'
    if re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)[eE][+-]?\d+', value):
        return 'exponent_number'
    if value.startswith('@'):
        return 'at_reference'
    if '$' in value:
        return 'parameter_atom'
    if ':' in value:
        return 'colon_atom'
    if '.' in value:
        return 'dotted_atom'
    return 'identifier_or_other_atom'

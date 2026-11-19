"""Frame JSON values incrementally; never depend on indentation or line breaks."""

import json
import re

from sttv.common.errors import BuildError
from sttv.common.json_io import unique_object, reject_constant

MARKS = re.compile(r'["\\{}\[\]]')
SPACE = re.compile(r'\S')


class Stream:
    def __init__(self, handle, chunk_size=1024 * 1024):
        self.handle, self.chunk_size = handle, chunk_size
        self.buffer, self.pos = '', 0

    def fill(self):
        self.buffer = self.buffer[self.pos:] + self.handle.read(self.chunk_size)
        self.pos = 0
        return bool(self.buffer)

    def peek(self):
        while True:
            match = SPACE.search(self.buffer, self.pos)
            if match:
                self.pos = match.start()
                return self.buffer[self.pos]
            self.pos = len(self.buffer)
            if not self.fill():
                return ''

    def take(self, character):
        if self.peek() != character:
            raise BuildError('json_read_error', f'Expected JSON delimiter {character}')
        self.pos += 1

    def raw(self, retain=True):
        """Scan a balanced object/array or scalar, including chunk-split escapes."""
        first = self.peek()
        if not first:
            raise BuildError('json_read_error', 'Unexpected end of JSON')
        if first not in '{["':
            parts = []
            while True:
                match = re.search(r'[\s,}\]]', self.buffer[self.pos:])
                end = self.pos + match.start() if match else len(self.buffer)
                parts.append(self.buffer[self.pos:end])
                self.pos = end
                if match or not self.fill():
                    return ''.join(parts)
        parts, depth, quoted, escaped = [], 0, False, False
        start = self.pos
        while True:
            for match in MARKS.finditer(self.buffer, self.pos):
                pos, char = match.start(), match.group()
                if escaped:
                    escaped = False
                    # An escape consumes exactly the immediately following character.
                    if pos == self.pos:
                        self.pos = pos + 1
                        continue
                if quoted:
                    if char == '\\':
                        escaped = True
                    elif char == '"':
                        quoted = False
                elif char == '"':
                    quoted = True
                elif char in '{[':
                    depth += 1
                elif char in '}]':
                    depth -= 1
                self.pos = pos + 1
                if depth == 0 and not quoted:
                    if retain:
                        parts.append(self.buffer[start:self.pos])
                    return ''.join(parts)
            if escaped and self.pos < len(self.buffer):
                escaped = False
            if retain:
                parts.append(self.buffer[start:])
            self.pos = len(self.buffer)
            if not self.fill():
                raise BuildError('json_read_error', 'Unterminated JSON value')
            start = 0

    def value(self):
        try:
            return json.loads(self.raw(), object_pairs_hook=unique_object, parse_constant=reject_constant)
        except (ValueError, RecursionError) as exc:
            raise BuildError('json_read_error', str(exc)) from exc

    def members(self):
        self.take('{')
        seen, first = set(), True
        while self.peek() != '}':
            if not first:
                self.take(',')
            key = self.value()
            if not isinstance(key, str) or key in seen:
                raise BuildError('duplicate_json_key', f'Invalid or duplicate member: {key}')
            seen.add(key)
            self.take(':')
            yield key
            first = False
        self.take('}')

    def indices(self):
        self.take('[')
        index = 0
        while self.peek() != ']':
            if index:
                self.take(',')
            yield index
            index += 1
        self.take(']')

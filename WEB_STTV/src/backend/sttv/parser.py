"""Small ordered parser for the supported Clausewitz script syntax."""

from dataclasses import dataclass

from .errors import BuildError


@dataclass(frozen=True)
class Token:
    text: str
    line: int
    quoted: bool = False


@dataclass
class Entry:
    key: str | None
    operator: str | None
    value: str | list
    line: int


OPERATORS = {"=", "<", ">", "<=", ">=", "!=", "?="}


def tokenize(text):
    index, line = 0, 1
    while index < len(text):
        char = text[index]
        if char.isspace() or (index == 0 and char == "\ufeff"):
            line += char == "\n"
            index += 1
            continue
        if char == "#":
            end = text.find("\n", index)
            index = len(text) if end < 0 else end
            continue
        start_line = line
        if char == '"':
            index += 1
            start = index
            while index < len(text):
                if text[index] == "\\":
                    if index + 1 >= len(text):
                        raise BuildError("unterminated_string", "Unterminated string",
                                         line=start_line)
                    line += text[index + 1] == "\n"
                    index += 2
                    continue
                if text[index] == '"':
                    yield Token(text[start:index], start_line, True)
                    index += 1
                    break
                line += text[index] == "\n"
                index += 1
            else:
                raise BuildError("unterminated_string", "Unterminated string",
                                 line=start_line)
            if index >= len(text) and text[-1:] != '"':
                raise BuildError("unterminated_string", "Unterminated string",
                                 line=start_line)
            continue
        pair = text[index:index + 2]
        if pair in OPERATORS:
            yield Token(pair, line)
            index += 2
        elif char in "{}=<>!":
            if char == "!":
                raise BuildError("invalid_operator", "Unexpected !", line=line)
            yield Token(char, line)
            index += 1
        else:
            start = index
            while index < len(text):
                char = text[index]
                if char.isspace() or char in '#"{}=<>!':
                    break
                if text[index:index + 2] == "?=":
                    break
                index += 1
            if index == start:
                raise BuildError("invalid_token", "Unexpected token", line=line)
            yield Token(text[start:index], line)


class Parser:
    def __init__(self, text):
        self.tokens = list(tokenize(text))
        self.index = 0

    def parse(self, nested=False):
        entries = []
        while self.index < len(self.tokens):
            token = self.tokens[self.index]
            self.index += 1
            if not token.quoted and token.text == "}":
                if nested:
                    return entries
                raise BuildError("unexpected_brace", "Unexpected closing brace",
                                 line=token.line)
            if not token.quoted and token.text in OPERATORS | {"{"}:
                raise BuildError("missing_key", "Expected a key or list value",
                                 line=token.line)
            following = (self.tokens[self.index]
                         if self.index < len(self.tokens) else None)
            if following and not following.quoted and following.text in OPERATORS:
                self.index += 1
                if self.index == len(self.tokens):
                    raise BuildError("missing_value", "Expected a value", line=token.line)
                value = self.tokens[self.index]
                self.index += 1
                if not value.quoted and value.text == "{":
                    result = self.parse(True)
                elif not value.quoted and value.text in OPERATORS | {"}"}:
                    raise BuildError("missing_value", "Expected a value", line=value.line)
                else:
                    result = value.text
                entries.append(Entry(token.text, following.text, result, token.line))
            else:
                entries.append(Entry(None, None, token.text, token.line))
        if nested:
            raise BuildError("unclosed_block", "Missing closing brace",
                             line=self.tokens[-1].line if self.tokens else 1)
        return entries


def parse_text(text):
    try:
        return Parser(text).parse()
    except RecursionError as exc:
        raise BuildError("nesting_limit", "Script nesting is too deep") from exc


def script_block(entries):
    return {"entries": [
        {"key": entry.key, "operator": entry.operator, "line": entry.line,
         "value": script_block(entry.value) if isinstance(entry.value, list)
         else entry.value}
        for entry in entries
    ]}

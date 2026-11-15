"""Parse ordered script structure using explicitly supplied syntax settings."""

from .delimiters import parameters
from .lexer import Lexer
from .inline import InlineScriptValue, expand_inline_script
from .nodes import (Assignment, Block, Conditional, Document, Formula, LogicalOperation, Scalar,
                    Source, TaggedBlock)


class Parser:
    def __init__(self, source, syntax):
        self.source, self.syntax = source, syntax
        self.lexer = Lexer(source, syntax)
        self.tokens, self.skipped_inline_scripts = [], []
        self.pending = None

    def read(self, opaque=False):
        while (token := self.lexer.next_token(opaque)) is not None:
            self.tokens.append(token)
            if token.kind not in ("space", "comment", "bom"):
                return token
        return None

    def peek(self):
        if self.pending is None:
            self.pending = self.read()
        return self.pending

    def take(self):
        token = self.peek()
        if token is None:
            self.source.fail("missing_value", "Expected a value", len(self.source.text))
        self.pending = None
        return token

    def inline(self, key):
        token = self.read(opaque=True)
        if token is None:
            self.source.fail("missing_value", "Expected an inline value", len(self.source.text))
        form = "block" if token.raw.startswith(self.syntax.lexical["block"]["open"]) else "reference"
        value = InlineScriptValue(token.raw, form, token.span)
        self.skipped_inline_scripts.append(self.span(key, token))
        return expand_inline_script(value, self.source)

    def span(self, start, end):
        return self.source.span(start.span.start, end.span.end)

    def scalar(self, token):
        quoted = token.kind == "string"
        width = len(self.syntax.lexical["string"]["quote"]) if quoted else 0
        text = token.raw[width:len(token.raw) - width] if quoted else token.raw
        fragments = parameters(self.source, token.span.start + width, token.span.end - width,
                               self.syntax, strict=not quoted)
        return Scalar(token.raw, text, quoted, fragments, token.span)

    def block(self, opening):
        items, closing = self.sequence("close", opening)
        return Block(items, self.span(opening, closing))

    def conditional(self, opening):
        spec = self.syntax.constructs["conditional"]
        header = opening.raw[len(spec["open"]):-len(spec["header_close"])]
        negated = header.startswith(spec["negation"])
        parameter = header.removeprefix(spec["negation"])
        items, closing = self.sequence("conditional_close", opening)
        return Conditional(parameter, negated, items, self.span(opening, closing))

    def atom_or_tag(self, token):
        scalar = self.scalar(token)
        following = self.peek()
        if following and following.kind == "open":
            if scalar.quoted or scalar.text not in self.syntax.constructs["tagged_blocks"]:
                self.source.fail("missing_operator", "Only configured tags may precede a block without an operator",
                                 token.span.start)
            block = self.block(self.take())
            return TaggedBlock(scalar, block, self.span(token, block))
        return scalar

    def value(self, token):
        if token.kind == "open":
            return self.block(token)
        if token.kind in ("atom", "string"):
            return self.atom_or_tag(token)
        if token.kind == "formula":
            spec = next(item for item in sorted(self.syntax.constructs["formulas"],
                                               key=lambda item: -len(item["open"]))
                        if token.raw.startswith(item["open"]))
            return Formula(token.raw, spec["open"],
                           token.raw[len(spec["open"]):-len(spec["close"])], token.span)
        self.source.fail("missing_value", "Expected a scalar, formula or block", token.span.start)

    def item(self, token):
        if token.kind == "conditional":
            return self.conditional(token)
        if token.kind == "open":
            if not self.syntax.constructs["anonymous_blocks"]:
                self.source.fail("disabled_form", "Anonymous blocks are disabled", token.span.start)
            return self.block(token)
        if token.kind not in ("atom", "string", "formula"):
            self.source.fail("unexpected_token", f"Unexpected token: {token.raw}", token.span.start)
        following = self.peek()
        if following and following.kind == "operator":
            if token.kind == "formula":
                self.source.fail("invalid_key", "A formula cannot be a key", token.span.start)
            operator = self.take().raw
            if token.kind == "atom" and operator == "=" and self.syntax.is_inline(token.raw):
                return self.inline(token)
            value = self.value(self.take())
            name = self.syntax.logical_name(token.raw) if token.kind == "atom" else None
            if (name is not None and operator == self.syntax.logical_operators["assignment_operator"]
                    and isinstance(value, Block)):
                return LogicalOperation(name, self.scalar(token), operator, value, self.span(token, value))
            return Assignment(self.scalar(token), operator, value, self.span(token, value))
        value = self.value(token)
        if not self.syntax.constructs["bare_values"]:
            self.source.fail("disabled_form", "Standalone values are disabled", token.span.start)
        return value

    def sequence(self, end=None, opening=None):
        items, forms = [], set()
        while self.peek() is not None:
            token = self.take()
            if token.kind == end:
                return items, token
            node = self.item(token)
            nodes = node if isinstance(node, list) else [node]
            items.extend(nodes)
            forms.update(isinstance(item, (Assignment, LogicalOperation)) for item in nodes)
            if len(forms) > 1 and not self.syntax.constructs["mixed_blocks"]:
                self.source.fail("disabled_form", "Mixed containers are disabled", token.span.start)
        if end:
            code = "unterminated_conditional" if end == "conditional_close" else "unterminated_block"
            self.source.fail(code, "Missing closing delimiter", opening.span.start)
        return items, None


def parse_text(text, syntax, source_name=None):
    source = Source(text, source_name)
    parser = Parser(source, syntax)
    try:
        items, _ = parser.sequence()
    except RecursionError:
        token = parser.peek()
        source.fail("nesting_depth", "Nesting exceeds parser capacity",
                    token.span.start if token else len(text))
    return Document(source, parser.tokens, items, parser.skipped_inline_scripts)

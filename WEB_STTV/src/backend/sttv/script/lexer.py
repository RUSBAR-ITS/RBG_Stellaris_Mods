"""Tokenize explicit syntax, retaining trivia and every original character."""

from .delimiters import comment_end, conditional_end, formula_end, parameter_at, string_end
from .nodes import Token
from .opaque import inline_value_end


class Lexer:
    def __init__(self, source, syntax):
        self.source, self.syntax = source, syntax
        lex, forms = syntax.lexical, syntax.constructs
        markers = [(lex["line_comment"], "comment"), (lex["string"]["quote"], "string"),
                   (lex["block"]["open"], "open"), (lex["block"]["close"], "close"),
                   (forms["conditional"]["open"], "conditional"),
                   (forms["conditional"]["body_close"], "conditional_close"),
                   *[(value, "operator") for value in lex["operators"]],
                   *[(value["open"], "formula") for value in forms["formulas"]]]
        self.markers = sorted(markers, key=lambda pair: -len(pair[0]))
        self.whitespace = set(lex["whitespace"])
        self.parameter = forms["parameters"]["open"]
        self.index = 0

    def marker(self, index):
        return next((pair for pair in self.markers if self.source.text.startswith(pair[0], index)), None)

    def tokens(self):
        while (token := self.next_token()) is not None:
            yield token

    def next_token(self, opaque=False):
        text, index = self.source.text, self.index
        if index < len(text):
            start, kind = index, "atom"
            if index == 0 and text[index] == "\ufeff":
                if not self.syntax.lexical["allow_initial_bom"]:
                    self.source.fail("unexpected_bom", "Initial BOM is disabled", index)
                kind, index = "bom", index + 1
            elif text[index] in self.whitespace:
                kind = "space"
                while index < len(text) and text[index] in self.whitespace:
                    index += 1
            elif text.startswith(self.syntax.lexical["line_comment"], index):
                kind, index = "comment", comment_end(text, index)
            elif opaque:
                kind, index = "opaque_value", inline_value_end(self.source, index, self.syntax)
            elif match := self.marker(index):
                marker, kind = match
                if kind == "comment":
                    index = comment_end(text, index)
                elif kind == "string":
                    index = string_end(self.source, index, self.syntax)
                elif kind == "formula":
                    spec = next(item for item in self.syntax.constructs["formulas"]
                                if item["open"] == marker)
                    index = formula_end(self.source, index, spec, self.syntax)
                elif kind == "conditional":
                    index = conditional_end(self.source, index, self.syntax)
                else:
                    index += len(marker)
            else:
                while index < len(text):
                    if text.startswith(self.parameter, index):
                        index = parameter_at(self.source, index, self.syntax, len(text)).span.end
                    elif text[index] in self.whitespace or self.marker(index):
                        break
                    elif text[index] == "\ufeff":
                        self.source.fail("unexpected_bom", "BOM is only allowed at the start", index)
                    else:
                        index += 1
            self.index = index
            return Token(kind, text[start:index], self.source.span(start, index))
        return None

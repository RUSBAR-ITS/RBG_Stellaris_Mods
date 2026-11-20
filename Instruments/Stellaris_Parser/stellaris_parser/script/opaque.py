"""Find an inline value boundary without tokenizing its internal syntax."""

from .delimiters import comment_end, string_end


def inline_value_end(source, start, syntax):
    text, lex = source.text, syntax.lexical
    quote, comment = lex["string"]["quote"], lex["line_comment"]
    opening, closing = lex["block"]["open"], lex["block"]["close"]
    if text.startswith(quote, start):
        return string_end(source, start, syntax)
    if text.startswith(opening, start):
        index, depth = start + len(opening), 1
        while index < len(text):
            if text.startswith(quote, index):
                index = string_end(source, index, syntax)
            elif text.startswith(comment, index):
                index = comment_end(text, index)
            elif text.startswith(opening, index):
                depth += 1
                index += len(opening)
            elif text.startswith(closing, index):
                depth -= 1
                index += len(closing)
                if not depth:
                    return index
            else:
                index += 1
        source.fail("unterminated_block", "Unterminated inline block", start)
    boundaries = [opening, closing, quote, comment, *lex["operators"],
                  syntax.constructs["conditional"]["body_close"]]
    index = start
    while index < len(text) and text[index] not in lex["whitespace"]:
        if any(text.startswith(marker, index) for marker in boundaries):
            break
        index += 1
    if index == start:
        source.fail("missing_value", "Expected an inline reference or block", start)
    return index

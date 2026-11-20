"""Read opaque delimited values without evaluating their content."""

from .nodes import Parameter


def string_end(source, start, syntax):
    spec, text = syntax.lexical["string"], source.text
    quote, escape = spec["quote"], spec["escape"]
    index = start + len(quote)
    while index < len(text):
        if text.startswith(quote, index):
            return index + len(quote)
        if text[index] in "\r\n" and not spec["multiline"]:
            source.fail("multiline_string", "Multiline strings are disabled", index)
        if text.startswith(escape, index):
            index += len(escape)
            if index >= len(text):
                break
            if text[index] in "\r\n" and not spec["multiline"]:
                source.fail("multiline_string", "Multiline strings are disabled", index)
            if text.startswith(quote, index):
                index += len(quote)
            else:
                index += len(escape) if text.startswith(escape, index) else 1
        else:
            index += 1
    source.fail("unterminated_string", "Unterminated string", start)


def parameter_at(source, start, syntax, limit, strict=True):
    spec, text = syntax.constructs["parameters"], source.text
    begin = start + len(spec["open"])
    end = text.find(spec["close"], begin, limit)
    if end < 0:
        if strict:
            source.fail("unterminated_parameter", "Unterminated parameter", start)
        return None
    name, separator, default = text[begin:end].partition(spec["default_separator"])
    if not name or any(char.isspace() for char in name):
        if strict:
            source.fail("invalid_parameter", "Expected a nonempty parameter name", start)
        return None
    end += len(spec["close"])
    return Parameter(name, default if separator else None, text[start:end], source.span(start, end))


def parameters(source, start, end, syntax, strict):
    cached = getattr(source, 'parameter_plan', {}).get((start, end))
    if cached is not None:
        return cached
    result, index = [], start
    opener = syntax.constructs["parameters"]["open"]
    while index < end:
        index = source.text.find(opener, index, end)
        if index < 0:
            break
        item = parameter_at(source, index, syntax, end, strict)
        if item:
            result.append(item)
            index = item.span.end
        else:
            index += len(opener)
    return tuple(result)


def comment_end(text, start):
    ends = [end for char in "\r\n" if (end := text.find(char, start)) >= 0]
    return min(ends, default=len(text))


def formula_end(source, start, spec, syntax):
    text, index = source.text, start + len(spec["open"])
    stack = [spec["close"]]
    forms = sorted(syntax.constructs["formulas"], key=lambda item: -len(item["open"]))
    while index < len(text):
        if text.startswith(syntax.lexical["string"]["quote"], index):
            index = string_end(source, index, syntax)
        elif text.startswith(syntax.lexical["line_comment"], index):
            index = comment_end(text, index)
        elif text.startswith(syntax.constructs["parameters"]["open"], index):
            index = parameter_at(source, index, syntax, len(text)).span.end
        elif found := next((item for item in forms if text.startswith(item["open"], index)), None):
            stack.append(found["close"])
            index += len(found["open"])
        elif text.startswith(stack[-1], index):
            index += len(stack.pop())
            if not stack:
                return index
        else:
            index += 1
    source.fail("unterminated_formula", "Unterminated formula", start)


def conditional_end(source, start, syntax):
    spec = syntax.constructs["conditional"]
    begin = start + len(spec["open"])
    end = source.text.find(spec["header_close"], begin)
    if end < 0:
        source.fail("unterminated_conditional", "Unterminated conditional header", start)
    name = source.text[begin:end].removeprefix(spec["negation"])
    if not name or any(char.isspace() for char in name):
        source.fail("invalid_conditional", "Expected a parameter name in conditional header", start)
    return end + len(spec["header_close"])

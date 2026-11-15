"""Independent reconstruction of meaningful tokens from syntax nodes."""

from sttv.script.nodes import Assignment, Block, Conditional, Formula, LogicalOperation, Scalar, TaggedBlock


def node_tokens(node, syntax):
    if isinstance(node, (Scalar, Formula)):
        return [node.raw]
    if isinstance(node, Assignment):
        return [node.key.raw, node.operator, *node_tokens(node.value, syntax)]
    if isinstance(node, LogicalOperation):
        return [node.name.raw, node.assignment_operator, *node_tokens(node.body, syntax)]
    if isinstance(node, TaggedBlock):
        return [node.tag.raw, *node_tokens(node.block, syntax)]
    children = [token for child in node.items for token in node_tokens(child, syntax)]
    if isinstance(node, Block):
        return [syntax.lexical["block"]["open"], *children, syntax.lexical["block"]["close"]]
    if isinstance(node, Conditional):
        spec = syntax.constructs["conditional"]
        header = spec["open"] + (spec["negation"] if node.negated else "") + node.parameter + spec["header_close"]
        return [header, *children, spec["body_close"]]
    raise AssertionError(type(node))


def check_document(document, syntax):
    text, index = document.source.text, 0
    for token in document.tokens:
        assert token.span.start == index
        assert text[token.span.start:token.span.end] == token.raw
        index = token.span.end
    assert index == len(text)
    assert ''.join(token.raw for token in document.tokens) == text
    skips = iter(document.skipped_inline_scripts)
    skip = next(skips, None)
    significant = []
    for token in document.tokens:
        while skip and token.span.start >= skip.end:
            skip = next(skips, None)
        if skip and skip.start <= token.span.start < skip.end:
            assert token.span.end <= skip.end
            continue
        if token.kind not in ('space', 'comment', 'bom'):
            significant.append(token.raw)
    reconstructed = [token for node in document.items for token in node_tokens(node, syntax)]
    assert reconstructed == significant
    return len(significant)

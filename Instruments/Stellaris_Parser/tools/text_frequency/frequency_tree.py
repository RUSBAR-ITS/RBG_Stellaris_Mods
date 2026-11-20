"""Count remaining AST text and verify it against tokens and skipped spans."""

from collections import Counter

from stellaris_parser.script.nodes import Assignment, Block, Conditional, Formula, LogicalOperation, Scalar, TaggedBlock
from stellaris_parser.script.nodes import InlineInvocation
from stellaris_parser.script.parser import parse_text
from stellaris_parser.script.traversal import walk
from variable_filter import exclusion_reason

EXCLUDED_TEXTS = frozenset({'yes', 'no'})
MINIMUM_COUNT = 2


def text_element(token, syntax):
    if token.kind in ('atom', 'formula'):
        return token.raw
    if token.kind == 'string':
        width = len(syntax.lexical['string']['quote'])
        return token.raw[width:-width]
    if token.kind == 'conditional':
        spec = syntax.constructs['conditional']
        header = token.raw[len(spec['open']):-len(spec['header_close'])]
        return header.removeprefix(spec['negation'])
    return None


def tree_text(node, logical, kinds):
    if isinstance(node, InlineInvocation):
        return
    if isinstance(node, Scalar):
        kinds['string' if node.quoted else 'atom'] += 1
        yield node.text
    elif isinstance(node, Formula):
        kinds['formula'] += 1
        yield node.raw
    elif isinstance(node, Assignment):
        yield from tree_text(node.key, logical, kinds)
        yield from tree_text(node.value, logical, kinds)
    elif isinstance(node, LogicalOperation):
        logical[node.name.span.start] = node.operator
        yield from tree_text(node.body, logical, kinds)
    elif isinstance(node, TaggedBlock):
        yield from tree_text(node.tag, logical, kinds)
        yield from tree_text(node.block, logical, kinds)
    elif isinstance(node, (Block, Conditional)):
        if isinstance(node, Conditional):
            kinds['conditional'] += 1
            yield node.parameter
        for child in node.items:
            yield from tree_text(child, logical, kinds)
    else:
        raise TypeError(f'Unsupported AST node: {type(node).__name__}')


def measure(text, syntax, name=None):
    document = parse_text(text, syntax, name, role="template")
    logical, kinds = {}, Counter()
    values = [value for node in document.items for value in tree_text(node, logical, kinds)]
    # Retrieve retained text independently from complete tokens and exact structural spans.
    skipped = [node.span for node in walk(document.items) if isinstance(node, InlineInvocation)]
    skips = iter(skipped)
    skip = next(skips, None)
    token_values, offset = [], 0
    for token in document.tokens:
        assert token.span.start == offset
        assert text[token.span.start:token.span.end] == token.raw
        offset = token.span.end
        while skip and token.span.start >= skip.end:
            skip = next(skips, None)
        if skip and skip.start <= token.span.start < skip.end:
            assert token.span.end <= skip.end
            continue
        if token.span.start in logical:
            continue
        value = text_element(token, syntax)
        if value is not None:
            token_values.append(value)
    assert offset == len(text)
    assert values == token_values
    assert sum(kinds.values()) == len(values)
    counts, excluded, variables, reasons = Counter(), Counter(), Counter(), Counter()
    for value in values:
        normalized = value.casefold()
        reason = exclusion_reason(value)
        if reason:
            variables[normalized] += 1
            reasons[reason] += 1
            continue
        (excluded if normalized in EXCLUDED_TEXTS else counts)[normalized] += 1
    details = {'logical_operator_counts': dict(Counter(logical.values())),
               'excluded_logical_operators': len(logical),
               'skipped_inline_scripts': len(skipped),
               'text_kinds': dict(kinds),
               'excluded_variable_counts': dict(variables),
               'excluded_variable_categories': dict(reasons),
               'excluded_variable_occurrences': sum(variables.values())}
    return counts, details, excluded


def frequency_rows(counts):
    return [{'text': text, 'count': count} for text, count in
            sorted(counts.items(), key=lambda item: (-item[1], item[0]))
            if count >= MINIMUM_COUNT]

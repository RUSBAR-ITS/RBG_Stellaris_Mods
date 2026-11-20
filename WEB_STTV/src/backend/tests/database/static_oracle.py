"""Independent oracle for the audited game's numeric static declarations."""

from dataclasses import fields, replace
import re

from stellaris_parser.script.nodes import Assignment, Located, Scalar
from stellaris_parser.script.parser import parse_text


def numeric_declarations(items):
    result = {}
    for node in items:
        if isinstance(node, Assignment) and node.key.text.startswith('@') and not node.key.quoted:
            assert isinstance(node.value, Scalar) and not node.value.quoted
            assert re.fullmatch(r'-?\d+(?:\.\d+)?', node.value.text), node
            assert node.key.text not in result
            result[node.key.text] = node.value
    return result


def shared_values(settings, manifest):
    assert settings.static_rules.options['prefix'] == '@'
    assert settings.static_rules.options['case_sensitive']
    values = {}
    for relative in manifest:
        doc = parse_text((settings.game / relative).read_text(encoding='utf-8-sig'),
                         settings.syntax, relative, role='template')
        added = numeric_declarations(doc.items)
        assert len(added) == len(doc.items)
        assert not values.keys() & added.keys()
        values.update(added)
    return values


def expected_items(document, shared):
    values = {**shared, **numeric_declarations(document.items)}
    replaced = 0

    def visit(node, role='value'):
        nonlocal replaced
        if isinstance(node, Scalar):
            if (role not in ('key', 'tag', 'name') and not node.quoted and not node.parameters
                    and re.fullmatch(r'@[A-Za-z_][A-Za-z0-9_]*', node.text)):
                environment = node.environment or document.source.environment
                local = numeric_declarations(environment.declarations.values()) if environment is not None else {}
                literal = {**values, **local}[node.text]
                replaced += 1
                return replace(node, raw=literal.raw, text=literal.text, quoted=False, parameters=())
            return node
        changes = {}
        for field in fields(node):
            child = getattr(node, field.name)
            if isinstance(child, Located):
                changes[field.name] = visit(child, field.name)
            elif field.name == 'items':
                changes[field.name] = [visit(item) for item in child]
        return replace(node, **changes)

    items = [node if isinstance(node, Assignment) and node.key.text.startswith('@') else visit(node)
             for node in document.items]
    return items, replaced

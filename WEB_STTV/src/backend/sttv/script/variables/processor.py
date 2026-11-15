"""Replace working scalars while preserving declarations, coordinates and history."""

from dataclasses import fields, replace

from ..nodes import Located, Scalar
from .rules import fail
from .table import Table


class Processor:
    def __init__(self, rules, shared, counts):
        self.rules, self.shared, self.counts = rules, shared, counts

    def apply(self, document):
        table = document.source.environment or self.prepare(document)
        try:
            document.items[:] = [node if self.rules.declaration(node) else self.visit(node, table)
                                 for node in document.items]
        except Exception as exc:
            exc.root_source = document.source.origin(0, 0)
            raise
        return document

    def prepare(self, document, count=True, table=None, resolve=True):
        table = table or Table(self.rules, self.shared)
        table.declarations.clear()
        table.resolved.clear()
        for node in document.items:
            if self.rules.declaration(node):
                table.add(node)
                if count:
                    self.counts['local_definitions'] += 1
        if resolve:
            table.resolve_all()
        document.source.environment = table
        return table

    def control(self, source, syntax):
        from ..parser import parse_source
        parsed = parse_source(source, syntax, specials=False)
        if len(parsed.items) != 1 or not isinstance(parsed.items[0], Scalar):
            return source.text
        node = parsed.items[0]
        name = self.rules.reference(node)
        return self.resolve(node, name, source.environment).text if name else source.text

    def resolve(self, node, name, fallback):
        table = node.environment or fallback
        if isinstance(table, tuple) or table is None:
            fail('ambiguous_static_environment', 'Cannot identify static reference environment', node)
        return table.resolve(name, node).value

    def visit(self, node, table, role='value'):
        if self.rules.declaration(node):
            fail('nested_static_declaration', 'Static declarations must be at document top level', node.key)
        if isinstance(node, Scalar):
            name = self.rules.reference(node) if role not in ('key', 'name', 'tag') else None
            if name is None:
                return node
            self.counts['references'] += 1
            value = self.resolve(node, name, table)
            self.counts['substituted'] += 1
            return replace(node, raw=value.raw, text=value.text, quoted=value.quoted, parameters=())
        changes = {}
        for field in fields(node):
            child = getattr(node, field.name)
            if isinstance(child, Located):
                updated = self.visit(child, table, field.name)
                if updated is not child:
                    changes[field.name] = updated
            elif field.name == 'items':
                updated = [self.visit(item, table) for item in child]
                if any(a is not b for a, b in zip(updated, child)):
                    changes[field.name] = updated
        return replace(node, **changes) if changes else node

"""Resolve isolated declaration tables without recursion or order dependence."""

from dataclasses import dataclass

from ..nodes import Scalar
from .rules import fail


@dataclass(frozen=True)
class Resolved:
    value: Scalar
    chain: tuple[str, ...]


class Table:
    def __init__(self, rules, shared=None):
        self.rules, self.shared = rules, shared or {}
        self.declarations, self.resolved = {}, {}

    def add(self, node):
        name = self.rules.reference(node.key)
        if name is None or node.operator != '=':
            fail('invalid_static_declaration', 'Expected an unquoted static name and =', node.key)
        if not isinstance(node.value, Scalar) or node.value.parameters:
            fail('unsupported_static_declaration', 'Expected a scalar without parameters', node.value)
        if name in self.declarations:
            earlier = self.declarations[name].key.origin
            place = f"{earlier['file']}:{earlier['span']['line']}:{earlier['span']['column']}"
            fail('duplicate_static_variable', f'Repeated {node.key.text}; first declared at {place}', node.key)
        self.declarations[name] = node

    def resolve(self, name, site):
        if name in self.resolved:
            return self.resolved[name]
        if name not in self.declarations and name in self.shared:
            result = self.shared[name]
            if len(result.chain) - 1 > self.rules.options['max_reference_depth']:
                fail('static_variable_depth', 'Reference depth exceeded: ' + ' -> '.join(result.chain), site)
            return result
        current, seen, chain = name, set(), []
        while True:
            declaration = self.declarations.get(current)
            display = declaration.key.text if declaration else current
            if current in seen:
                fail('static_variable_cycle', ' -> '.join([*chain, display]), site)
            seen.add(current)
            if declaration is None:
                if current not in self.shared:
                    fail('unknown_static_variable', 'Unknown reference: ' + ' -> '.join([*chain, display]), site)
                result = self.shared[current]
                chain.extend(result.chain)
                value = result.value
            else:
                chain.append(display)
                value = declaration.value
            if len(chain) - 1 > self.rules.options['max_reference_depth']:
                fail('static_variable_depth', 'Reference depth exceeded: ' + ' -> '.join(chain), site)
            following = self.rules.reference(value) if declaration is not None else None
            if following is None:
                result = Resolved(value, tuple(chain))
                self.resolved[name] = result
                return result
            current = following

    def resolve_all(self):
        for name, node in self.declarations.items():
            self.resolve(name, node.value)
        return self.resolved

    def signature(self, name):
        """Identify every declaration in an already resolved reference chain."""
        origins = []
        while name in self.declarations:
            declaration = self.declarations[name]
            origins.append(declaration.key.origin)
            name = self.rules.reference(declaration.value)
            if name is None:
                return origins
        resolved = self.shared[name]
        return [*origins, resolved.value.origin, resolved.chain]

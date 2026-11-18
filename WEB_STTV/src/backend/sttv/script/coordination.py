"""Coordinate mixed calls, resource bounds, and final insertion addresses."""

from dataclasses import fields, replace
from pathlib import PurePosixPath

from sttv.common.errors import BuildError
from .nodes import Assignment, Block, InlineInvocation, Located, Scalar
from .traversal import sequences
from .metrics import measured_application


class Coordinator:
    def __init__(self, templates, options, report=None, library=None, variables=None, exceptions=None):
        self.templates, self.options, self.report = templates, options, report
        self.library, self.variables = library, variables
        self.exceptions = exceptions
        self.records, self.stack, self.warnings, self.sources = [], [], [], {}
        self.counts = dict(encountered=0, expanded=0, failed=0, template_files=0, max_depth=0)
        self.parameter_counts = dict(defaults=0, retained_fragments=0, discarded_fragments=0)
        self.max_depth, self.created, self.preparing, self.root_only = 0, 0, False, False

    @measured_application
    def expand(self, document, syntax, root_only=False):
        self.records, self.stack, self.sources, self.created = [], [], {}, 0
        self.root_source = document.source.origin(0, 0)
        table = self.variables.prepare(document, count=False, resolve=False) if self.variables else None
        try:
            if not root_only and self.variables and any(isinstance(n, InlineInvocation) for n in document.items):
                from .parser import parse_source
                prepared = parse_source(document.source, syntax)
                preparer = type(self)(self.templates, self.options, variables=self.variables, exceptions=self.exceptions)
                preparer.preparing = True
                preparer.expand(prepared, syntax, root_only=True)
                table = prepared.source.environment
                self.variables.prepare(prepared, table=table)
            elif self.variables and not root_only:
                self.variables.prepare(document, table=table)
            self.root_only = root_only
            patterns = self.library.options['root_definition_files'] if self.library else []
            definition_root = self.root_source['root'] == 'STELLARIS_ROOT' and any(
                PurePosixPath(self.root_source['file'].casefold()).match(pattern.casefold()) for pattern in patterns)
            self.sequence(document.items, document.source, syntax, definition_root)
            if self.variables and root_only:
                self.variables.prepare(document, count=not self.preparing, table=table)
            from .addresses import finalize
            finalize(document, self.records)
            document.metadata['expansions'].extend(self.records)
            return document
        finally:
            self.counts['template_files'] = len(self.templates.manifest)
            self.root_only = False

    def sequence(self, items, source, syntax, definition_root=False):
        previous = [record for record in self.records if record.get('_items') is items]
        boundaries, result = [0], []
        for node in items:
            current = self.sources.get(id(node), source)
            is_definition = definition_root and isinstance(node, Assignment) and isinstance(node.value, Block)
            definition = self.library.find(node) if self.library and not self.root_only and not is_definition else None
            if isinstance(node, InlineInvocation) or definition is not None:
                first, index = len(self.records), len(result)
                expanded = self.call(node, current, syntax, definition, definition_root)
                self.records[first].update(_items=items, _index=index, _count=len(expanded))
                for child in self.records[first + 1:]:
                    if child.get('_items') is expanded:
                        child['_items'], child['_index'] = items, child['_index'] + index
                result.extend(expanded)
            else:
                if not self.root_only:
                    node = self.children(node, current, syntax)
                result.append(node)
            boundaries.append(len(result))
        for record in previous:
            start, count = record['_index'], record['_count']
            record['_index'] = boundaries[start]
            record['_count'] = boundaries[start + count] - boundaries[start]
        items[:] = result

    def children(self, node, source, syntax, role='value'):
        if self.variables and self.variables.rules.declaration(node):
            return node
        if isinstance(node, Scalar) and role not in ('key', 'name', 'tag') and self.library:
            from .values.expansion import reference_source
            if self.library.value_options is not None:
                payload = reference_source(self, node, source, syntax)
                if payload is not None:
                    return self.call(node, source, syntax, payload=payload)
        changes = {}
        for field in fields(node):
            value = getattr(node, field.name)
            if field.name == 'items':
                self.sequence(value, source, syntax)
            elif isinstance(value, Located):
                updated = self.children(value, source, syntax, field.name)
                if updated is not value:
                    changes[field.name] = updated
        return replace(node, **changes) if changes else node

    def control(self, source, syntax):
        return self.variables.control(source, syntax) if self.variables else source.text

    def missing_parameter(self, record, options):
        return self.exceptions.missing(self, record, options) if self.exceptions else None

    def remember(self, document):
        for _, items in sequences(document.items):
            self.sources.update((id(node), document.source) for node in items)

    def account(self, items):
        def count(node):
            total = 1
            for field in fields(node):
                value = getattr(node, field.name)
                if isinstance(value, Located):
                    total += count(value)
                elif field.name == 'items':
                    total += sum(count(child) for child in value)
            return total
        self.account_extra(sum(count(node) for node in items))

    def account_extra(self, count):
        self.created += count
        if self.library and self.created > self.library.options['max_expanded_nodes']:
            raise BuildError('expansion_size', 'Expanded node budget exceeded')

    def unused(self, bindings, used, target, record, node):
        if unused := sorted(bindings.keys() - used):
            code = 'unused_inline_argument' if record['kind'] == 'inline_script' else 'unused_scripted_argument'
            message = f"{target}: unused arguments: {', '.join(unused)}"
            self.warnings.append(dict(code=code, message=message, call_id=record['id']))
            if self.report is not None:
                self.report.add('warning', code, 'expansion', message, source=node.origin['root'],
                                file=node.origin['file'], line=node.origin['span']['line'])

    def call(self, node, source, syntax, definition=None, definition_root=False, payload=None):
        from .calls import call
        from .metrics import ACTIVE
        metrics = ACTIVE.get()
        if metrics:
            metrics.count('plan_uses')
        return call(self, node, source, syntax, definition, definition_root, payload)

    def identify(self, frame, identity, target, code):
        frame.update(identity=identity, template=target)
        if any(parent.get('identity') == identity for parent in self.stack[:-1]):
            raise BuildError(code, f'Recursive expansion: {target}')

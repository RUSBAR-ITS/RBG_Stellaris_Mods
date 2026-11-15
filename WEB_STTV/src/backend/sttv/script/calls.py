"""Shared invocation frames and errors across all expansion kinds."""

from sttv.common.errors import BuildError


def call(self, node, source, syntax, definition=None, definition_root=False, payload=None):
    from .scripted.expansion import expand_named
    kind = 'script_value' if payload is not None else definition.kind if definition else 'inline_script'
    counts = self.counts if kind == 'inline_script' else self.library.counts[kind]
    counts['encountered'] += 1
    prefix = kind.removesuffix('_script') if not definition else kind
    record = dict(id=f"{prefix}_{counts['encountered']}", kind=kind,
                  parent_id=self.stack[-1]['id'] if self.stack else node.origin.get('expansion_id'),
                  call_site=node.origin)
    self.records.append(record)
    frame = dict(id=record['id'], kind=kind, template=None, call_site=node.origin)
    self.stack.append(frame)
    self.max_depth = max(self.max_depth, len(self.stack))
    self.counts['max_depth'] = max(self.counts['max_depth'], len(self.stack))
    try:
        if self.library and len(self.stack) > self.library.options['max_call_depth']:
            raise BuildError('expansion_depth', 'Mixed call depth exceeded')
        if payload is not None:
            from .values.expansion import expand_value
            result = expand_value(self, node, payload, syntax, record, frame)
        elif definition:
            identity = (kind, self.library.key(definition.name))
            self.identify(frame, identity, definition.name, 'scripted_cycle')
            result = expand_named(self, definition, node, source, syntax, record)
        else:
            result = self.inline_call(node, source, syntax, record, frame, definition_root)
        counts['expanded'] += 1
        return result
    except (BuildError, OSError, ValueError, RecursionError) as exc:
        counts['failed'] += 1
        if not isinstance(exc, BuildError):
            exc = BuildError('expansion_error', str(exc))
        if not hasattr(exc, 'call_chain'):
            exc.call_chain = [{k: v for k, v in item.items() if k != 'identity'} for item in self.stack]
            exc.root_source = self.root_source
            exc.provenance = getattr(exc, 'provenance', node.origin)
        raise exc
    finally:
        self.stack.pop()

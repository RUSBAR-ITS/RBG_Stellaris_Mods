"""Expand inline files using the shared mixed-call coordinator."""

from copy import copy

from sttv.common.errors import BuildError
from ..coordination import Coordinator
from ..parser import parse_source
from .binding import invocation
from .substitution import substitute


class Expansion(Coordinator):
    def inline_call(self, node, source, syntax, record, frame, definition_root=False):
        if len(self.stack) > self.options['max_depth']:
            raise BuildError('inline_depth', 'Inline expansion depth exceeded')
        path, raw, arguments, bindings = invocation(node, source, syntax, self.options)
        identity, relative, _ = self.templates.identity(path.text)
        record.update(target=dict(file=relative),
                      invocation=dict(operator='=', form=node.form if node.form == 'reference' else 'arguments',
                                      raw=source.original_text(node.value_span.start, node.value_span.end)),
                      arguments=arguments, directives=[])
        self.identify(frame, ('inline_script', identity), relative, 'inline_cycle')
        template = copy(self.templates.read(path.text))
        template.environment = source.environment_at(node.span.start, node.span.end)
        expanded, used = substitute(template, bindings, syntax, self.options,
                                    None if self.preparing else record['id'],
                                    lambda text: self.control(text, syntax), self.parameter_counts)
        document = parse_source(expanded, syntax)
        self.account(document.items)
        self.remember(document)
        self.sequence(document.items, expanded, syntax, definition_root)
        self.unused(bindings, used, relative, record, node)
        return document.items


def expand_inline_script(node, source, syntax, expansion):
    return expansion.call(node, source, syntax)

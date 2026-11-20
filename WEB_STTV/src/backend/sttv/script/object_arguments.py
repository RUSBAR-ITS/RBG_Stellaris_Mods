"""Derive an approved missing argument from the original enclosing object."""

from sttv.common.errors import BuildError
from .nodes import Assignment, Block, Scalar, Source
from .inlining.text import slice_source


def derive(context, action, config_file, call_id, parameter):
    options = action['parameter_from_object']
    for frame in reversed(context.stack[:-1]):
        bindings = context.argument_bindings.get(frame['id'], {})
        if parameter in bindings:
            context.forwarded_arguments.setdefault(frame['id'], set()).add(parameter)
            return bindings[parameter], f'{frame["id"]}:{parameter}'
    document = context.exception_document
    site = next((frame['call_site'] for frame in context.stack
                 if frame['call_site']['root'] == context.root_source['root']
                 and frame['call_site']['file'] == context.root_source['file']), None)
    owners = [] if site is None else [node for node in context.exception_objects
        if node.origin['span']['start'] <= site['span']['start'] < node.origin['span']['end']]
    if len(owners) != 1:
        raise BuildError('source_exception_object', 'Cannot identify one enclosing source object')
    owner = owners[0]
    fields = [n for n in owner.value.items if isinstance(n, Assignment)
              and n.key.text == options['field'] and n.operator == '=']
    if len(fields) != 1 or not isinstance(fields[0].value, Block):
        raise BuildError('source_exception_object', f'{owner.key.text}: expected one {options["field"]} list')
    values = fields[0].value.items
    if not values or any(not isinstance(n, Scalar) or n.parameters or n.text not in options['allowed_values']
                         for n in values):
        raise BuildError('source_exception_object', f'{owner.key.text}: unknown or invalid {options["field"]}')
    label = f'{document.source.file}:{owner.key.text}/{options["field"]}'
    if len({n.text for n in values}) == 1:
        value = values[0]
        width = 1 if value.quoted else 0
        return slice_source(document.source, value.span.start + width, value.span.end - width), label
    return Source(options['multiple_literal'], config_file, 'PRODUCT_ROOT', call_id), label + ' -> ' + config_file

"""Explicit lexical plan records; game text remains unrestricted."""

from .helpers import NULL, STRING, TEXT, BOOL, obj, array, mapping, union, ref

INTEGER = {'type': 'integer', 'minimum': 0}
TOKEN_KINDS = ['atom', 'space', 'comment', 'bom', 'string', 'open', 'close',
               'operator', 'formula', 'conditional', 'conditional_close']


def reference():
    return obj({'$ref': INTEGER})


def plan():
    span = obj({name: INTEGER for name in ('start', 'end', 'line', 'column', 'end_line', 'end_column')})
    parameter = obj({'name': STRING, 'default': union(STRING, NULL), 'raw': STRING, 'span': span})
    token = obj({'start': INTEGER, 'end': INTEGER, 'kind': {'enum': TOKEN_KINDS},
                 'parameters': array(parameter)})
    return obj({'tokens': array(token), 'parameter_count': INTEGER, 'conditional': BOOL,
                'items': union(NULL, array(reference()))})


def fields(cls, names):
    result = {name: ref('value') for name in names}
    plain_text = {'raw', 'text', 'opener', 'parameter', 'operator', 'assignment_operator', 'form'}
    reference_fields = {'span', 'value_span', 'key', 'tag', 'block', 'value'}
    for name in names:
        if name in plain_text:
            result[name] = STRING
        elif name in reference_fields:
            result[name] = reference()
        elif name in ('quoted', 'negated'):
            result[name] = BOOL
        elif name == 'items':
            result[name] = array(reference())
        elif name == 'parameters':
            result[name] = obj({'$tuple': array(reference())})
        elif name == 'origin':
            result[name] = union(NULL, mapping(ref('value')))
        elif name in ('default', 'scope'):
            result[name] = union(STRING, NULL)
        elif name == 'environment':
            result[name] = union(NULL, reference(), obj({'$tuple': array(reference())}))
    if 'body' in names:
        result['body'] = STRING if cls.__name__ == 'Formula' else reference()
    if 'name' in names:
        result['name'] = reference() if cls.__name__ == 'LogicalOperation' else STRING
    if cls.__name__ == 'Token':
        result['kind'] = TEXT
    if cls.__name__ == 'Resolved':
        result['chain'] = obj({'$tuple': array(STRING)})
    if cls.__name__ == 'Table':
        result = {name: mapping(reference()) for name in names}
    if cls.__name__ in ('Source', 'MappedSource'):
        result.update(text=STRING, file=union(STRING, NULL), root=TEXT, call_id=NULL,
                      plan=union(NULL, plan()))
    if cls.__name__ == 'MappedSource':
        result.update(base=reference(), pieces=array(reference()))
    if cls.__name__ == 'Piece':
        result.update(text=STRING, start=INTEGER, end=INTEGER, source=reference(),
                      argument=union(NULL, reference()))
    if cls.__name__ == 'Definition':
        result.update(name=TEXT, kind={'enum': ['scripted_effect', 'scripted_trigger', 'script_value']},
                      source=reference(), node=reference())
    if cls.__name__ == 'Span':
        result = {name: INTEGER for name in names}
    return result

"""Encode a whitelisted definition graph, preserving shared source environments."""

from dataclasses import fields

from document_package.errors import BuildError
from stellaris_parser.script import nodes
from stellaris_parser.script.inlining.text import MappedSource, Piece
from stellaris_parser.script.scripted.index import Definition
from stellaris_parser.script.variables.table import Table, Resolved

CLASSES = {cls.__name__: cls for cls in (nodes.Source, MappedSource, Table, Piece, Definition, Resolved,
    nodes.Span, nodes.Token, nodes.Parameter, nodes.Scalar, nodes.Formula, nodes.Block,
    nodes.ScriptValue, nodes.TaggedBlock, nodes.Conditional, nodes.Assignment,
    nodes.LogicalOperation, nodes.InlineInvocation, nodes.ScriptedTriggerTest)}
SOURCE_FIELDS = ('text', 'file', 'root', 'call_id', 'environment', 'plan')


def attributes(cls):
    if cls is MappedSource:
        return (*SOURCE_FIELDS, 'pieces', 'base')
    if cls is nodes.Source:
        return SOURCE_FIELDS
    if cls is Table:
        return ('shared', 'declarations', 'resolved')
    return tuple(field.name for field in fields(cls))


def encode(value):
    objects, seen = [], {}

    def visit(item):
        if item is None or isinstance(item, (str, int, float, bool)):
            return item
        if isinstance(item, dict):
            return {key: visit(child) for key, child in item.items()}
        if isinstance(item, list):
            return [visit(child) for child in item]
        if isinstance(item, tuple):
            return {'$tuple': [visit(child) for child in item]}
        cls = type(item)
        if cls.__name__ not in CLASSES or CLASSES[cls.__name__] is not cls:
            raise BuildError('library_object_type', f'Unsupported library object: {cls.__name__}')
        identity = id(item)
        if identity not in seen:
            seen[identity] = len(objects)
            row = {'type': cls.__name__, 'fields': {}}
            objects.append(row)
            row['fields'] = {key: visit(getattr(item, key, None)) for key in attributes(cls)}
        return {'$ref': seen[identity]}

    root = visit(value)
    return {'root': root, 'objects': objects}


def decode(graph, rules):
    objects = []
    for row in graph['objects']:
        cls = CLASSES.get(row['type'])
        if cls is None or set(row['fields']) != set(attributes(cls)):
            raise BuildError('library_object_type', f'Invalid library object: {row["type"]}')
        objects.append(cls.__new__(cls))

    def visit(item):
        if isinstance(item, list):
            return [visit(child) for child in item]
        if isinstance(item, dict):
            if '$ref' in item:
                index = item['$ref']
                if set(item) != {'$ref'} or type(index) is not int or not 0 <= index < len(objects):
                    raise BuildError('library_reference', f'Invalid library reference: {index}')
                return objects[index]
            if '$tuple' in item:
                if set(item) != {'$tuple'}:
                    raise BuildError('library_reference', 'Malformed tuple record')
                return tuple(visit(child) for child in item['$tuple'])
            return {key: visit(child) for key, child in item.items()}
        return item

    for obj, row in zip(objects, graph['objects']):
        for name, value in row['fields'].items():
            object.__setattr__(obj, name, visit(value))
    from .references import validate_objects
    validate_objects(objects)
    for obj in objects:
        if isinstance(obj, nodes.Source):
            if not isinstance(obj.text, str):
                raise BuildError('library_source', 'Invalid prepared source text')
            obj.lines = [0, *(i + 1 for i, char in enumerate(obj.text) if char == '\n')]
            if isinstance(obj, MappedSource):
                obj.starts, offset = [], 0
                for piece in obj.pieces:
                    obj.starts.append(offset)
                    offset += len(piece.text)
                if offset != len(obj.text):
                    raise BuildError('library_source', 'Mapped source length mismatch')
            if obj.plan is not None:
                validate_plan(obj)
                from stellaris_parser.script.prepared import install
                install(obj)
        elif isinstance(obj, Table):
            obj.rules = rules
    return visit(graph['root'])


def validate_plan(source):
    plan = source.plan
    if set(plan) != {'tokens', 'parameter_count', 'conditional', 'items'}:
        raise BuildError('library_plan', 'Invalid prepared plan fields')
    end = 0
    parameters = 0
    for row in plan['tokens']:
        if row['start'] != end or not end < row['end'] <= len(source.text):
            raise BuildError('library_plan', 'Invalid prepared token range')
        end = row['end']
        for parameter in row['parameters']:
            span = parameter['span']
            if not row['start'] <= span['start'] < span['end'] <= row['end']:
                raise BuildError('library_plan', 'Parameter escapes its token')
        parameters += len(row['parameters'])
    if end != len(source.text):
        raise BuildError('library_plan', 'Incomplete prepared token stream')
    if parameters != plan['parameter_count']:
        raise BuildError('library_plan', 'Parameter count differs from the plan')
    conditional = any(row['kind'] == 'conditional' for row in plan['tokens'])
    if conditional != plan['conditional'] or plan['items'] is not None and (parameters or conditional):
        raise BuildError('library_plan', 'Constant/conditional plan classification mismatch')

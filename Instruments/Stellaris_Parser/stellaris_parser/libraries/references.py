"""Check prepared reference targets before exposing a loaded graph."""

from document_package.errors import BuildError
from stellaris_parser.script.nodes import Source, Located, Assignment
from stellaris_parser.script.inlining.text import MappedSource, Piece
from stellaris_parser.script.scripted.index import Definition
from stellaris_parser.script.variables.table import Table, Resolved
from stellaris_parser.script import nodes


def require(condition, message):
    if not condition:
        raise BuildError('library_reference', message)


def validate_objects(objects):
    for obj in objects:
        if isinstance(obj, Source):
            environment = obj.environment
            require(environment is None or isinstance(environment, Table)
                    or isinstance(environment, tuple) and all(isinstance(e, Table) for e in environment),
                    'Invalid source environment')
            if obj.plan and obj.plan['items'] is not None:
                require(all(isinstance(item, Located) for item in obj.plan['items']), 'Invalid plan nodes')
        if isinstance(obj, MappedSource):
            require(isinstance(obj.base, Source) and all(isinstance(p, Piece) for p in obj.pieces),
                    'Invalid mapped source references')
        elif isinstance(obj, Piece):
            require(isinstance(obj.source, Source) and (obj.argument is None or isinstance(obj.argument, Source)),
                    'Invalid source piece reference')
            require(0 <= obj.start <= obj.end <= len(obj.source.text), 'Invalid source piece range')
        elif isinstance(obj, Definition):
            require(isinstance(obj.source, Source) and isinstance(obj.node, Assignment), 'Invalid definition targets')
        elif isinstance(obj, Table):
            require(isinstance(obj.shared, dict) and all(isinstance(v, Resolved) for v in obj.shared.values()),
                    'Invalid shared declarations')
            require(isinstance(obj.declarations, dict)
                    and all(isinstance(v, Assignment) for v in obj.declarations.values()), 'Invalid declarations')
            require(isinstance(obj.resolved, dict) and all(isinstance(v, Resolved) for v in obj.resolved.values()),
                    'Invalid resolved declarations')
        validate_node(obj)
    validate_source_graph(objects)
    validate_node_graph(objects)


def validate_node(obj):
    if isinstance(obj, (Located, nodes.Token, nodes.Parameter)):
        require(isinstance(obj.span, nodes.Span), 'Invalid node span reference')
    if isinstance(obj, nodes.Scalar):
        require(all(isinstance(p, nodes.Parameter) for p in obj.parameters), 'Invalid parameter reference')
    if isinstance(obj, nodes.InlineInvocation):
        require(isinstance(obj.value_span, nodes.Span), 'Invalid inline value span')
    if isinstance(obj, nodes.Assignment):
        require(isinstance(obj.key, nodes.Scalar) and isinstance(obj.value, Located), 'Invalid assignment references')
    if isinstance(obj, nodes.LogicalOperation):
        require(isinstance(obj.name, nodes.Scalar) and isinstance(obj.body, nodes.Block), 'Invalid logical references')
    if isinstance(obj, (nodes.ScriptValue, nodes.ScriptedTriggerTest)):
        require(isinstance(obj.body, nodes.Block), 'Invalid calculation or trigger body')
    if isinstance(obj, nodes.TaggedBlock):
        require(isinstance(obj.tag, nodes.Scalar) and isinstance(obj.block, nodes.Block), 'Invalid tagged block')
    if isinstance(obj, Resolved):
        require(isinstance(obj.value, nodes.Scalar), 'Invalid resolved scalar')
    if isinstance(obj, (nodes.Block, nodes.Conditional)):
        require(all(isinstance(item, Located) for item in obj.items), 'Invalid container child reference')


def validate_node_graph(objects):
    from dataclasses import fields
    finished = set()
    for root in objects:
        if not isinstance(root, Located) or id(root) in finished:
            continue
        pending, active = [(root, False)], set()
        while pending:
            node, closing = pending.pop()
            identity = id(node)
            if closing:
                active.remove(identity)
                finished.add(identity)
            elif identity not in finished:
                require(identity not in active, 'Cyclic prepared syntax tree')
                active.add(identity)
                pending.append((node, True))
                for field in fields(node):
                    if field.name in ('origin', 'environment'):
                        continue
                    value = getattr(node, field.name)
                    children = value if isinstance(value, (list, tuple)) else (value,)
                    pending.extend((child, False) for child in children if isinstance(child, Located))


def validate_source_graph(objects):
    finished = set()
    for root in objects:
        if not isinstance(root, Source) or id(root) in finished:
            continue
        pending, active = [(root, False)], set()
        while pending:
            source, closing = pending.pop()
            identity = id(source)
            if closing:
                active.remove(identity)
                finished.add(identity)
            elif identity not in finished:
                require(identity not in active, 'Cyclic prepared source ancestry')
                active.add(identity)
                pending.append((source, True))
                if isinstance(source, MappedSource):
                    children = [source.base, *(p.source for p in source.pieces),
                                *(p.argument for p in source.pieces if p.argument is not None)]
                    pending.extend((child, False) for child in children)

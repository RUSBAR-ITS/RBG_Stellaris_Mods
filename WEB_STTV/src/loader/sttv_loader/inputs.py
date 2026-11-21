"""Configured source selection and object boundaries."""

from dataclasses import dataclass
from pathlib import Path

from document_package.errors import BuildError
from document_package.json_io import read_json
from document_package.package import Package

from .settings import collection_name


@dataclass(frozen=True)
class Source:
    path: Path
    collection: str
    provenance: str | None
    identity: str
    field: str | None
    root_types: tuple
    containers: tuple


class Inputs:
    def __init__(self, options, config_directory):
        root = config_directory / options['input_root']
        self.history = collection_name(options['history_collection'])
        self.names = [self.history]
        self.sources = []
        paths = set()
        for entry in options['sources']:
            path = (root / entry['path']).resolve()
            identity = entry['identity']
            if identity not in ('key', 'field', 'anonymous', 'fragments', 'file', 'package'):
                raise BuildError('invalid_source', f'Unknown identity mode at {path}: {identity}')
            if path in paths or (identity == 'field' and not entry.get('field')):
                raise BuildError('invalid_source', f'Ambiguous or incomplete source: {path}')
            paths.add(path)
            name = collection_name(entry['collection'])
            provenance = None
            if identity != 'package':
                provenance = collection_name(entry['provenance'])
                self.names.append(provenance)
            self.names.append(name)
            self.sources.append(Source(path, name, provenance, identity, entry.get('field'),
                                       tuple(entry.get('root_types', [])), tuple(entry.get('containers', []))))
        if not paths or len(set(self.names)) != len(self.names) or any(n.startswith('sttv__') for n in self.names):
            raise BuildError('invalid_collections', 'Expected sources with distinct, non-reserved collection names')

    def records(self):
        roots = {s.path: s for s in self.sources}
        for source in self.sources:
            if source.identity == 'package':
                package = Package(source.path)
                for batch in package.batches():
                    for document in batch:
                        yield InputRecord(source.collection, document)
                continue
            if source.path.is_file():
                files = [source.path]
            elif source.path.is_dir():
                files = sorted(source.path.rglob('*.json'))
            else:
                raise BuildError('missing_source', f'Missing input: {source.path}')
            for path in files:
                owner = next(roots[p] for p in (path, *path.parents) if p in roots)
                if owner == source:
                    yield from script_records(source, path, self.history)


@dataclass(frozen=True)
class InputRecord:
    collection: str
    document: dict
    provenance: str | None = None


def blocks(items, prefix, containers, root_types):
    for index, node in enumerate(items):
        if node.get('kind') != 'assignment' or node['value']['kind'] != 'block':
            continue
        key = node['key']['text']
        pointer = f'{prefix}/{index}'
        if containers:
            if key == containers[0]:
                yield from blocks(node['value']['items'], pointer + '/value/items', containers[1:], root_types)
        elif not root_types or key in root_types:
            yield pointer, index, node


def script_records(spec, path, history):
    data = read_json(path)
    source = {key: data['source'][key] for key in ('root', 'file')}
    if not all(isinstance(v, str) and v for v in source.values()) or not isinstance(data['items'], list):
        raise BuildError('invalid_document', f'Invalid script source or items in {path}')
    yield InputRecord(history, {'_id': source, 'metadata': data['metadata']})
    if spec.identity == 'file':
        yield InputRecord(spec.collection, {'_id': source, 'source': source, 'pointer': '/items',
                                            'tree': data['items']}, spec.provenance)
        return
    identity_field = spec.field.casefold() if spec.identity == 'field' else None
    for pointer, index, node in blocks(data['items'], '/items', spec.containers, spec.root_types):
        identifier = node['key']['text']
        if identity_field is not None:
            values = [item['value'].get('text') for item in node['value']['items']
                      if item.get('kind') == 'assignment' and item['key']['text'].casefold() == identity_field]
            if len(values) > 1:
                raise BuildError('ambiguous_object_id', f'{path}{pointer}: multiple fields match {spec.field!r}')
            if len(values) != 1 or not isinstance(values[0], str) or not values[0]:
                raise BuildError('missing_object_id', f'{path}{pointer}: expected one {spec.field}')
            identifier = values[0]
        elif spec.identity in ('anonymous', 'fragments'):
            identifier = {**source, 'item': index}
        yield InputRecord(spec.collection, {'_id': identifier, 'source': source, 'pointer': pointer,
                                            'tree': node}, spec.provenance)

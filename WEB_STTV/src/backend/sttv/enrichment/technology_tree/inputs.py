"""Read the existing set and build compact records with stable source references."""

from collections import defaultdict
from fnmatch import fnmatchcase
from pathlib import PurePosixPath

from sttv.common.errors import BuildError
from .ast import compact, fields, scalar
from sttv.storage.objects import object_row
from sttv.storage.references import node_ref


def record_for(kind, document_id, pointer, node):
    row = object_row(kind, document_id, pointer, node)
    if row is None:
        return None
    body = compact(node['value'])
    identity = row['id'] if row['id'] is not None else document_id + pointer
    return {'id': identity, 'type': row['type'], 'body': body,
            'source': node_ref(kind, document_id, pointer)}


def technology_input(settings, reader):
    records, targets, documents = [], {}, {}
    spec = settings.targets['selection']
    directory = PurePosixPath(settings.selection_directory)
    for document in reader.iter_documents('technologies'):
        identifier = document['document_id']
        documents[identifier] = document
        file = PurePosixPath(document['source']['file'])
        selected = (file.is_relative_to(directory) if spec['recursive'] else file.parent == directory)
        if not selected or not fnmatchcase(file.name, spec['pattern']):
            continue
        for ni, node in enumerate(document['items']):
            pointer = f'/items/{ni}'
            record = record_for('technologies', identifier, pointer, node)
            if record is not None and fields(record['body'], 'tier'):
                records.append(record)
                targets[(identifier, pointer)] = node
    if not records:
        raise BuildError('no_technologies', 'Technology target selection is empty')
    return documents, records, targets


class Catalog:
    def __init__(self, records):
        self.records = records
        self.by_id = {}
        for kind, rows in records.items():
            index = defaultdict(list)
            for row in rows:
                index[row['id']].append(row)
            self.by_id[kind] = index

    def resolve(self, kind, key, *, fragments=False, required=False):
        rows = self.by_id.get(kind, {}).get(key, [])
        if not rows and required:
            raise BuildError('missing_object', f'Unresolved object: {kind}/{key}')
        if len(rows) > 1 and not fragments:
            raise BuildError('ambiguous_object', f'Ambiguous object: {kind}/{key}')
        return rows if fragments else rows[0] if rows else None

    def rows(self, kind):
        return self.records[kind]

"""Pin a manifest and lazily read only requested immutable documents."""

from collections import defaultdict
from pathlib import Path
from time import perf_counter

from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from .manifest import check
from .references import node_ref
from .settings import confined
from .reading import read, signature


class Reader:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.root = self.path.parent
        self.manifest = check(read_json(self.path))
        self.descriptors, self.paths, self.objects, self.index = {}, {}, {}, {}
        self.cache, self.verified = {}, {}
        self.bytes, self.seconds = 0, 0.0
        for kind, dataset in self.manifest['datasets'].items():
            objects, index = defaultdict(list), defaultdict(list)
            for row in dataset['objects']:
                objects[row['document_id']].append(row)
                if row['id'] is not None:
                    index[row['id']].append(node_ref(kind, row['document_id'], row['pointer']))
            self.index[kind] = index
            for descriptor in dataset['documents']:
                key = kind, descriptor['document_id']
                path = confined(self.root, descriptor['path'])
                if not path.is_file():
                    raise BuildError('missing_document', f'Missing document: {path}')
                self.paths[key], self.descriptors[key], self.objects[key] = path, descriptor, objects[key[1]]

    def iter_objects(self, kind):
        return iter(self.manifest['datasets'][kind]['objects'])

    def resolve_object(self, kind, identifier):
        return list(self.index[kind].get(identifier, []))

    def document_ids(self, kind):
        return [row['document_id'] for row in self.manifest['datasets'][kind]['documents']]

    def project(self, kind, identifier, extract=None, *, cache_key=None, full=False):
        key = kind, identifier
        cache = key, cache_key, full
        if cache_key is not None and cache in self.cache:
            self.check_document(key)
            return self.cache[cache]
        started = perf_counter()
        result, verification = read(self.paths[key], kind, self.descriptors[key], self.objects[key], extract, full)
        self.bytes += verification['bytes']
        self.seconds += perf_counter() - started
        self.verified[key] = verification['signature']
        if cache_key is not None:
            self.cache[cache] = result
        return result

    def read_document(self, kind, identifier):
        return self.project(kind, identifier, full=True)

    def iter_documents(self, kind):
        for identifier in self.document_ids(kind):
            yield self.read_document(kind, identifier)

    def check_document(self, key):
        if signature(self.paths[key]) != self.verified[key]:
            raise BuildError('changed_input', f'Used document changed: {self.paths[key]}')

    def check_snapshot(self):
        current = check(read_json(self.path))
        if current['snapshot_revision'] != self.manifest['snapshot_revision']:
            raise BuildError('changed_manifest', 'The published snapshot changed during this operation')
        for key in self.verified:
            self.check_document(key)

    def coverage(self):
        return {'declared': len(self.paths), 'verified': len(self.verified),
                'not_checked': len(self.paths) - len(self.verified), 'bytes_read': self.bytes,
                'documents': [{'database': kind, 'document_id': identifier,
                    'status': 'verified' if (kind, identifier) in self.verified else 'not_checked'}
                    for kind, identifier in self.paths]}


def open_set(manifest_path):
    return Reader(manifest_path)

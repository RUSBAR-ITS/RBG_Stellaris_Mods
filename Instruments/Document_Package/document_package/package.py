"""Portable package of ordered, content-addressed JSON document batches."""

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

from .errors import BuildError
from .json_io import read_json, reject_constant, unique_object

FORMAT = 'stellaris.documents.v1'


def confined(directory, relative):
    root = Path(directory).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or path == root:
        raise BuildError('unsafe_path', f'Path escapes package: {relative}')
    return path


def formatted(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
    try:
        temporary.write_bytes(content)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def save_json(path, value):
    atomic_write(path, formatted(value))


def write_batch(directory, documents):
    content = formatted(documents)
    digest = hashlib.sha256(content).hexdigest()
    relative = f'batches/{digest}.json'
    atomic_write(confined(directory, relative), content)
    return {'path': relative, 'sha256': digest, 'count': len(documents)}


def check_manifest(value):
    if (not isinstance(value, dict) or value.get('format') != FORMAT
            or not isinstance(value.get('collection'), str) or not value['collection']):
        raise BuildError('invalid_package', 'Unknown document package or missing logical collection')
    batches = value.get('batches')
    if not isinstance(batches, list) or type(value.get('documents')) is not int:
        raise BuildError('invalid_package', 'Invalid package counts')
    for batch in batches:
        if (not isinstance(batch, dict) or not isinstance(batch.get('sha256'), str)
                or not re.fullmatch('[0-9a-f]{64}', batch['sha256'])
                or batch.get('path') != f"batches/{batch['sha256']}.json"
                or type(batch.get('count')) is not int or batch['count'] < 1):
            raise BuildError('invalid_package', 'Invalid batch descriptor')
    if sum(b['count'] for b in batches) != value['documents']:
        raise BuildError('invalid_package', 'Package count mismatch')


def commit_manifest(directory, collection, batches):
    manifest = {'format': FORMAT, 'collection': collection, 'batches': batches,
                'documents': sum(batch['count'] for batch in batches)}
    check_manifest(manifest)
    save_json(confined(directory, 'manifest.json'), manifest)


class Package:
    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        self.manifest = read_json(confined(self.directory, 'manifest.json'))
        check_manifest(self.manifest)

    def batches(self):
        for descriptor in self.manifest['batches']:
            data = confined(self.directory, descriptor['path']).read_bytes()
            if hashlib.sha256(data).hexdigest() != descriptor['sha256']:
                raise BuildError('invalid_batch', f"Checksum mismatch: {descriptor['path']}")
            rows = json.loads(data, object_pairs_hook=unique_object, parse_constant=reject_constant)
            if (not isinstance(rows, list) or len(rows) != descriptor['count']
                    or any(not isinstance(row, dict) or '_id' not in row for row in rows)):
                raise BuildError('invalid_batch', f"Invalid documents: {descriptor['path']}")
            yield rows

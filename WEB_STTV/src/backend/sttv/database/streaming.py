"""Write validated document fragments and merge bytes without reparsing trees."""

import hashlib
import json
import os
import tempfile
from pathlib import Path

from sttv.common.errors import BuildError
from sttv.common.timing import measure
from .validation import DatabaseValidator, FORMAT, FORMAT_VERSION

ALGORITHM = 'sttv.document_hashes.v1'
CANONICAL = json.JSONEncoder(sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
FORMATTED = json.JSONEncoder(sort_keys=True, ensure_ascii=False, indent=2, allow_nan=False)


def canonical_hash(value):
    digest = hashlib.sha256()
    for chunk in CANONICAL.iterencode(value):
        digest.update(chunk.encode('utf-8'))
    return digest.hexdigest()


def write_fragment(document, path, index, metrics):
    times = metrics['timings']
    with measure(times, 'validation'):
        nodes = DatabaseValidator().document(document, index)
    metrics['validated_documents'] += 1
    metrics['documents'].append({'source': document['source']['file'], 'nodes': nodes,
                                'status': 'success', 'seconds': times['validation']})
    with measure(times, 'hashing'):
        content_hash = canonical_hash(document)
    temporary = path.with_suffix('.partial')
    digest, size = hashlib.sha256(), 0
    try:
        with measure(times, 'write'), temporary.open('wb') as handle:
            raw = b'    '
            handle.write(raw)
            digest.update(raw)
            size += len(raw)
            for chunk in FORMATTED.iterencode(document):
                raw = chunk.replace('\n', '\n    ').encode('utf-8')
                handle.write(raw)
                digest.update(raw)
                size += len(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    return {'path': str(path), 'bytes': size, 'content_hash': content_hash,
            'shard_hash': digest.hexdigest(), 'nodes': nodes, 'source_identity':
            [document['source']['root'], document['source']['file'].casefold()]}


def merge_fragments(destination, results, metrics):
    header = {'format': FORMAT, 'format_version': FORMAT_VERSION}
    DatabaseValidator().container(dict(header, documents=[None] * len(results)))
    content_hash = canonical_hash(dict(header, identity_algorithm=ALGORITHM, documents=[
        {'index': row['index'], 'content_hash': row['fragment']['content_hash']} for row in results]))
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with measure(metrics['timings'], 'merge'), tempfile.NamedTemporaryFile(
                mode='wb', dir=destination.parent, prefix=destination.name + '.', suffix='.tmp', delete=False) as output:
            temporary = Path(output.name)
            output.write(b'{\n  "documents": [\n')
            for index, row in enumerate(results):
                fragment = row['fragment']
                digest, size = hashlib.sha256(), 0
                if index:
                    output.write(b',\n')
                with Path(fragment['path']).open('rb') as source:
                    while chunk := source.read(1024 * 1024):
                        output.write(chunk)
                        digest.update(chunk)
                        size += len(chunk)
                if size != fragment['bytes'] or digest.hexdigest() != fragment['shard_hash']:
                    raise BuildError('fragment_checksum', f'Damaged fragment: {row["source"]}')
            output.write(('\n  ],\n' + FORMATTED.encode(header)[2:] + '\n').encode('utf-8'))
            output.flush()
            os.fsync(output.fileno())
        return temporary, content_hash
    except BaseException:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise

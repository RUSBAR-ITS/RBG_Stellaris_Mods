"""Write one structurally checked document and its compact index."""

import hashlib
import os
from pathlib import Path

from sttv.database.validation import DatabaseValidator
from sttv.common.timing import measure
from .identity import document_id, source_hash, FORMATTED
from .objects import index_document
from .references import finalize


def prepare(document, kind):
    identifier = document_id(kind, document['source'])
    finalize(document, kind, identifier)
    return {'format': 'sttv.parse_document', 'format_version': 1, 'database': kind,
            'document_id': identifier, **{k: document[k] for k in ('source', 'items', 'metadata')}}


def write_document(document, path, kind, metrics, *, validate=True):
    document = prepare(document, kind)
    identifier = document['document_id']
    with measure(metrics['timings'], 'validation'):
        nodes = 0
        if validate:
            validator = DatabaseValidator()
            validator.container(document)
            nodes = validator.document(document)
        objects = index_document(kind, identifier, document['items'], document['source'])
    if validate:
        metrics['validated_documents'] += 1
        metrics['documents'].append({'source': document['source']['file'], 'nodes': nodes,
                                    'status': 'success', 'seconds': metrics['timings']['validation']})
    with measure(metrics['timings'], 'hashing'):
        content_hash = source_hash(document)
    digest, size = hashlib.sha256(), 0
    temporary = Path(path).with_suffix('.partial')
    try:
        with measure(metrics['timings'], 'write'), temporary.open('wb') as handle:
            for chunk in FORMATTED.iterencode(document):
                raw = chunk.encode('utf-8')
                handle.write(raw)
                digest.update(raw)
                size += len(raw)
            handle.write(b'\n')
            digest.update(b'\n')
            size += 1
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    file_hash = digest.hexdigest()
    descriptor = {'document_id': identifier, 'source': document['source'], 'byte_size': size,
                  'file_hash': file_hash, 'source_hash': content_hash, 'item_count': len(document['items'])}
    return {'path': str(path), 'bytes': size, 'content_hash': content_hash, 'shard_hash': file_hash,
            'nodes': nodes, 'source_identity': [document['source']['root'], document['source']['file'].casefold()],
            'descriptor': descriptor, 'objects': objects}

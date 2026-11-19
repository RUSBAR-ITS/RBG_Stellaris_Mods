"""Canonical identities for immutable source documents and published snapshots."""

import hashlib
import json

from sttv.common.datasets import REGISTRY
from sttv.common.errors import BuildError

ENCODER = json.JSONEncoder(sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
FORMATTED = json.JSONEncoder(sort_keys=True, ensure_ascii=False, indent=2, allow_nan=False)
SOURCE_ALGORITHM = 'sttv.document_source.v1'


def digest(value):
    result = hashlib.sha256()
    for chunk in ENCODER.iterencode(value):
        result.update(chunk.encode('utf-8'))
    return result.hexdigest()


def relative(value):
    if (not isinstance(value, str) or not value or '\\' in value or ':' in value
            or any(part in ('', '.', '..') for part in value.split('/'))):
        raise BuildError('unsafe_storage_path', f'Invalid relative path: {value}')
    return value


def document_id(kind, source):
    return digest([kind, source['root'], relative(source['file']).casefold()])


def registry_revision():
    return digest(REGISTRY)


def source_hash(document):
    result = dict(document)
    result['items'] = []
    for node in document['items']:
        if 'technology_tree' in node.get('enrichments', {}):
            node = dict(node)
            node['enrichments'] = {k: v for k, v in node['enrichments'].items() if k != 'technology_tree'}
            if not node['enrichments']:
                del node['enrichments']
        result['items'].append(node)
    return digest({'algorithm': SOURCE_ALGORITHM, 'document': result})


def source_revision(documents):
    return digest([[d['document_id'], d['source_hash']] for d in documents])


def set_revision(manifest):
    return digest({'algorithm': 'sttv.dataset_sources.v1', 'registry_revision': manifest['registry_revision'],
                   'datasets': {k: v['source_revision'] for k, v in sorted(manifest['datasets'].items())}})


def snapshot_revision(manifest):
    return digest({k: v for k, v in manifest.items() if k != 'snapshot_revision'})

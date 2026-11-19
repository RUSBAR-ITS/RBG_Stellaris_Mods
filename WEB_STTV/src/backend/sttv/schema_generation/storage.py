"""Contracts for immutable documents and generated set manifests."""

from .helpers import HASH, TEXT, NULL, RELATIVE, BOOL, array, obj, union, mapping
from .configuration import selection
from . import database, technology_tree, assets
from sttv.common.datasets import KINDS

COUNT = {'type': 'integer', 'minimum': 0}


def node_ref():
    return obj({'database': {'enum': list(KINDS)}, 'document_id': HASH,
                'pointer': {'type': 'string', 'pattern': r'^/items/\d+(?:/.*)?$'}})


def configuration():
    return obj({'format_version': {'const': 1}, **{key: RELATIVE for key in
        ('directory', 'manifest', 'documents', 'staging_directory', 'report')}, 'parallel': selection()})


def descriptor():
    return obj({'document_id': HASH, 'source': database.definitions()['document']['properties']['source'],
                'path': RELATIVE, 'byte_size': COUNT, 'file_hash': HASH, 'source_hash': HASH, 'item_count': COUNT})


def object_row():
    return obj({'id': union(TEXT, NULL), 'type': TEXT, 'document_id': HASH,
                'pointer': {'type': 'string', 'pattern': r'^/items/\d+$'}})


def manifest():
    dataset = obj({'source_revision': HASH, 'documents': array(descriptor()), 'objects': array(object_row())})
    result = obj({'format': {'const': 'sttv.database_manifest'}, 'format_version': {'const': 1},
                  'set_id': HASH, 'snapshot_revision': HASH, 'registry_revision': HASH,
                  'datasets': obj({kind: dataset for kind in KINDS})})
    result['properties']['technology_tree'] = technology_tree.metadata()
    result['properties']['presentation'] = assets.manifest()
    return result


def document():
    definitions = database.definitions()
    result = obj({'format': {'const': 'sttv.parse_document'}, 'format_version': {'const': 1},
                  'database': {'enum': list(KINDS)}, 'document_id': HASH,
                  **definitions['document']['properties']})
    result['$defs'] = definitions
    return result


def report():
    return obj({'format': {'const': 'sttv.storage_report'}, 'format_version': {'const': 1},
        'status': {'enum': ['success', 'failed']}, 'manifest': TEXT, 'snapshot_revision': union(HASH, NULL),
        'coverage': {'type': 'object'}, 'timings': mapping({'type': 'number', 'minimum': 0}),
        'diagnostics': array({'type': 'object'}), 'published': BOOL})

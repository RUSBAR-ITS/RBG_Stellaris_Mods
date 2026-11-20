"""Generate and validate an object inventory without opening document contents."""

from sttv.common.datasets import KINDS
from sttv.common.errors import BuildError
from sttv.common.schema import validate_schema
from .identity import document_id, registry_revision, source_revision, set_revision, snapshot_revision, relative
from .objects import check_objects
from sttv.common.object_selection import pointer_indices


def create(members, acquisition=None):
    from sttv.enrichment.acquisition.storage import empty
    result = {'format': 'sttv.database_manifest', 'format_version': 2,
              'acquisition': acquisition if acquisition is not None else empty(),
              'registry_revision': registry_revision(), 'datasets': {}}
    for kind in KINDS:
        rows = sorted(members[kind], key=lambda r: r['descriptor']['source']['file'].casefold())
        documents = [r['descriptor'] for r in rows]
        result['datasets'][kind] = {'documents': documents, 'objects': [o for r in rows for o in r['objects']],
                                    'source_revision': source_revision(documents)}
    return finalize(result)


def finalize(manifest):
    for dataset in manifest['datasets'].values():
        dataset['source_revision'] = source_revision(dataset['documents'])
    manifest['set_id'] = set_revision(manifest)
    manifest['snapshot_revision'] = snapshot_revision(manifest)
    check(manifest)
    return manifest


def check(manifest):
    if isinstance(manifest, dict) and isinstance(manifest.get('datasets'), dict):
        missing = set(KINDS) - manifest['datasets'].keys()
        if missing:
            raise BuildError('incompatible_registry', f'Prepare a new database set; missing catalogs: {sorted(missing)}')
    validate_schema(manifest, 'database_manifest.schema.json')
    if manifest['registry_revision'] != registry_revision():
        raise BuildError('incompatible_registry', 'Prepare a new database set; object identity rules have changed')
    if manifest['set_id'] != set_revision(manifest) or manifest['snapshot_revision'] != snapshot_revision(manifest):
        raise BuildError('manifest_revision', 'Manifest revision does not match its content')
    paths, identities = set(), set()
    for kind, dataset in manifest['datasets'].items():
        documents = dataset['documents']
        if documents != sorted(documents, key=lambda d: d['source']['file'].casefold()):
            raise BuildError('document_order', f'Noncanonical document order: {kind}')
        by_id = {}
        for row in documents:
            identifier = row['document_id']
            path = relative(row['path']).casefold()
            if path in paths or identifier in identities or identifier != document_id(kind, row['source']):
                raise BuildError('duplicate_source', f'Repeated path or invalid document identity: {kind}/{identifier}')
            paths.add(path)
            identities.add(identifier)
            by_id[identifier] = row
        check_objects(kind, dataset['objects'], by_id)
        ordering = {row['document_id']: i for i, row in enumerate(documents)}
        order = []
        for row in dataset['objects']:
            document = by_id[row['document_id']]
            indices = pointer_indices(kind, row['pointer'], document['source'])
            if indices is None or indices[0] >= document['item_count']:
                raise BuildError('invalid_object_index', f'Invalid object selector: {kind}/{row}')
            order.append((ordering[row['document_id']], indices))
        if order != sorted(order):
            raise BuildError('object_order', f'Noncanonical object order: {kind}')
        if dataset['source_revision'] != source_revision(documents):
            raise BuildError('source_revision', f'Invalid source revision: {kind}')
    from .assets import check_assets
    check_assets(manifest, paths)
    from sttv.enrichment.acquisition.storage import check
    check(manifest['acquisition'], paths)
    return manifest

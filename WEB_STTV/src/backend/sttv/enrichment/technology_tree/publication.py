"""Publish only changed documents and switch a complete combination atomically."""

from copy import deepcopy
from contextlib import nullcontext

from sttv.common.errors import BuildError
from sttv.common.timing import performance
from sttv.storage.manifest import finalize
from sttv.storage.writing import write_document


def publish(reader, documents, changed, combo, metadata, settings, publication):
    manifest = deepcopy(reader.manifest)
    dataset = manifest['datasets']['technologies']
    for index, descriptor in enumerate(dataset['documents']):
        identifier = descriptor['document_id']
        if identifier not in changed:
            continue
        fragment = write_document(documents[identifier], publication.directory / f'{identifier}.json',
                                  'technologies', performance(), validate=False)
        if fragment['descriptor']['source_hash'] != descriptor['source_hash']:
            raise BuildError('changed_source', f'Tree enrichment changed source data: {identifier}')
        row = publication.accept(fragment, 'technologies')
        dataset['documents'][index] = row['descriptor']
    manifest.setdefault('technology_tree', {'format_version': 1, 'combinations': {}})['combinations'][combo] = metadata
    finalize(manifest)
    if manifest['set_id'] != reader.manifest['set_id']:
        raise BuildError('changed_source', 'Tree enrichment changed the source set identity')
    def verify():
        settings.check_snapshot()
        reader.check_snapshot()
    with settings.commit_guard() if settings.commit_guard else nullcontext():
        publication.publish(manifest, verify)
    return manifest

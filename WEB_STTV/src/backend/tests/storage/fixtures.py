"""Publish synthetic documents through the production manifest protocol."""

from copy import deepcopy

from sttv.common.datasets import KINDS
from sttv.common.json_io import read_json
from sttv.common.timing import performance
from sttv.storage import open_set
from sttv.storage.manifest import create, finalize
from sttv.storage.publication import Publication
from sttv.storage.settings import load
from sttv.storage.writing import write_document


def publish(variables, documents, *, storage_config=None, validate=False):
    settings = load(variables, storage_config)
    with Publication(settings) as publication:
        members = {kind: [] for kind in KINDS}
        old = read_json(settings.manifest) if settings.manifest.exists() else None
        for kind in KINDS:
            if kind not in documents and old:
                continue
            for number, document in enumerate(documents.get(kind, [])):
                fragment = write_document(document, publication.directory / f'{kind}-{number}.json',
                                          kind, performance(), validate=validate)
                members[kind].append(publication.accept(fragment, kind))
        from sttv.enrichment.acquisition.storage import empty
        from sttv.enrichment.acquisition.configuration import load as acquisition_options
        from sttv.storage.identity import digest
        index = empty()
        options, _ = acquisition_options({'base': 'product', 'path': 'config/enrichment/acquisition/sources.json'}, settings.root.parent)
        index['configuration_revision'] = options['revision']
        index['revision'] = digest({k: v for k, v in index.items() if k not in ('revision', 'statistics')})
        manifest = create(members, index)
        if old:
            for kind in KINDS:
                if kind not in documents:
                    manifest['datasets'][kind] = deepcopy(old['datasets'][kind])
            if 'technology_tree' in old:
                manifest['technology_tree'] = deepcopy(old['technology_tree'])
            finalize(manifest)
        publication.publish(manifest)
    return settings.manifest


def documents(path, kind='technologies'):
    return list(open_set(path).iter_documents(kind))

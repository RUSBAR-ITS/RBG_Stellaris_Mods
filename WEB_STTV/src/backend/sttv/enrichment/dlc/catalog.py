"""Resolve catalog IDs to exact game predicate names without ownership inference."""

from sttv.common.errors import BuildError
from sttv.enrichment.technology_tree.ast import scalar
from sttv.enrichment.technology_tree.revisions import digest


def read_catalog(reader, rules):
    kind = rules['catalog']['database']
    documents, names = {}, {}
    for row in reader.iter_objects(kind):
        identifier = row['document_id']
        if identifier not in documents:
            documents[identifier] = reader.read_document(kind, identifier)
        node = documents[identifier]
        for part in row['pointer'].strip('/').split('/'):
            node = node[int(part)] if isinstance(node, list) else node[part]
        name = scalar(node['value'], rules['catalog']['name_field'])
        if not name or name in names.values() or row['id'] in names:
            raise BuildError('dlc_catalog_conflict', f'Missing or duplicated DLC identity: {row["id"]}/{name}')
        names[row['id']] = name
    return names


def profile(names, enabled):
    if not isinstance(enabled, list) or any(not isinstance(key, str) for key in enabled):
        raise BuildError('invalid_dlc_profile', 'Enabled DLC must be an array of catalog IDs')
    unknown = set(enabled) - names.keys()
    if unknown:
        raise BuildError('unknown_dlc', f'Unknown DLC IDs: {sorted(unknown)}')
    return {'known': sorted(names), 'enabled': sorted(set(enabled)), 'catalog_revision': digest(names)}

"""Replace one complete named combination while retaining other enrichments."""

from .revisions import script_nodes
from sttv.common.errors import BuildError


def address(tech):
    return tech['source']['document_id'], tech['source']['pointer']


def stored(manifest, documents, targets, technologies, combo):
    metadata = manifest.get('technology_tree', {}).get('combinations', {}).get(combo)
    records = {}
    for key, tech in technologies.items():
        node = targets[address(tech)]
        row = node.get('enrichments', {}).get('technology_tree', {}).get(combo)
        if row is not None:
            records[key] = row
    selected_nodes = {id(targets[address(t)]) for t in technologies.values()}
    for document in documents.values():
        for root in document['items']:
            for node in script_nodes(root):
                if (combo in node.get('enrichments', {}).get('technology_tree', {})
                        and id(node) not in selected_nodes):
                    raise BuildError('invalid_tree_target', 'Stored combination contains obsolete or nested targets')
    return metadata, records


def attach(documents, targets, technologies, combo, results):
    desired = {id(targets[address(tech)]): results[key] for key, tech in technologies.items()}
    changed = set()
    for identifier, document in documents.items():
        for root in document['items']:
            for node in script_nodes(root):
                value = desired.get(id(node))
                old = node.get('enrichments', {}).get('technology_tree', {}).get(combo)
                if old == value:
                    continue
                changed.add(identifier)
                if value is not None:
                    node.setdefault('enrichments', {}).setdefault('technology_tree', {})[combo] = value
                else:
                    enrichments = node['enrichments']
                    enrichments['technology_tree'].pop(combo)
                    if not enrichments['technology_tree']:
                        del enrichments['technology_tree']
                    if not enrichments:
                        del node['enrichments']
    return changed

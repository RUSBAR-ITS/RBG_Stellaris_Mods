"""Link configured catalog entries to separate descriptor documents by exact name."""

from pathlib import Path

from sttv.common.datasets import definition
from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.common.object_selection import selected_nodes, source_role
from sttv.enrichment.localization.targets import one_field
from sttv.parallel.localization import Localizations
from sttv.storage.writing import write_document


def scalar(items, field, address, required=True):
    matches = [n for n in items if n['kind'] == 'assignment' and n['key']['text'] == field]
    if not matches and not required:
        return None
    if len(matches) != 1 or matches[0]['value']['kind'] != 'scalar' or not matches[0]['value']['text']:
        raise BuildError('descriptor_field', f'{address}: expected one nonempty {field}')
    return matches[0]['value']['text']


def relationships(kind, documents):
    config = definition(kind)['descriptorLink']
    catalog, descriptors, nodes = {}, {}, {}
    for document in documents:
        identifier = document['document_id']
        if source_role(kind, document['source']) == 'descriptor':
            name = scalar(document['items'], config['matchField'], document['source']['file'])
            if name in descriptors:
                raise BuildError('descriptor_conflict', f'{name}: {descriptors[name]["source"]} and {document["source"]}')
            descriptors[name] = document
        else:
            for pointer, node in selected_nodes(kind, document['items'], document['source']):
                name = scalar(node['value']['items'], config['matchField'], document['source']['file'] + pointer)
                if name in catalog:
                    raise BuildError('catalog_conflict', f'{name}: {catalog[name]} and {(identifier, pointer)}')
                catalog[name] = identifier, pointer
                nodes[name] = node
    if not catalog:
        raise BuildError('missing_catalog', f'{kind}: no catalog entries selected')
    return catalog, descriptors, nodes


def decorate_targets(kind, targets, descriptors):
    config = definition(kind)['descriptorLink']
    for target in targets:
        name = one_field(target.node, config['matchField'], target.path)[0]
        descriptor = descriptors.get(name)
        if descriptor is None:
            continue
        key = scalar(descriptor['items'], config['localizationField'], descriptor['source']['file'], False)
        if key:
            target.candidates['name'] = [key]
            target.candidate_sources[key] = {'database': kind, 'document_id': descriptor['document_id']}


def prepare(kind, results, local, build, report):
    documents = [read_json(row['fragment']['path']) for row in results]
    catalog, descriptors, nodes = relationships(kind, documents)
    for name, node in nodes.items():
        descriptor = descriptors.get(name)
        refs = [{'database': kind, 'document_id': descriptor['document_id']}] if descriptor else []
        node.setdefault('enrichments', {})['dlc'] = {'descriptors': refs}
    extras = sorted(descriptors.keys() - catalog.keys())
    for name in extras:
        build.add('warning', 'unmatched_descriptor', 'linking', name,
                  source='STELLARIS_ROOT', file=descriptors[name]['source']['file'])
    cache, identities = Localizations(), {}
    def decorate(targets):
        decorate_targets(kind, targets, descriptors)
    for ordinal, (result, document) in enumerate(zip(results, documents)):
        if source_role(kind, document['source']) != 'descriptor':
            result['localization_files'] = cache.apply(document, local, ordinal, report, identities,
                                                      build.data['performance']['timings'], decorate)
        result['fragment'] = write_document(document, Path(result['fragment']['path']), kind, build.data['performance'])
        build.data['counts']['nodes'] += result['fragment']['nodes']
    return {'catalog_entries': len(catalog), 'descriptors': len(descriptors),
            'matched_pairs': len(catalog.keys() & descriptors.keys()),
            'without_descriptor': len(catalog.keys() - descriptors.keys()),
            'unmatched_descriptors': len(extras), 'conflicts': 0}


def verify(kind, documents):
    catalog, descriptors, nodes = relationships(kind, documents)
    config = definition(kind)['descriptorLink']
    for name, node in nodes.items():
        descriptor = descriptors.get(name)
        expected = [{'database': kind, 'document_id': descriptor['document_id']}] if descriptor else []
        if node.get('enrichments', {}).get('dlc', {}).get('descriptors') != expected:
            raise BuildError('descriptor_reference', f'{catalog[name]}: incorrect descriptor references')
        for language in node.get('enrichments', {}).get('localization', {}).values():
            for value in language.values():
                fallback = value.get('fallback')
                if fallback and fallback['kind'] == 'dlc_descriptor':
                    if (fallback['source_ref'] not in expected or not descriptor
                            or value['key'] != scalar(descriptor['items'], config['localizationField'], name)):
                        raise BuildError('descriptor_reference', f'{name}: incorrect localization descriptor')

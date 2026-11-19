"""Resolve technology/variant images and collect category identifiers."""

from sttv.common.errors import BuildError


def fields(node):
    return {item.get('key', {}).get('text'): item.get('value', {})
            for item in node.get('value', {}).get('items', []) if item.get('kind') == 'assignment'}


def text(field):
    return field.get('text') if field.get('kind') == 'scalar' else None


def attach(document, settings, images, categories, report):
    if document['source']['file'].rsplit('/', 1)[0] != settings.localization.selection_directory:
        return False
    keys, changed = settings.options['fields'], False

    def record(node, name, base_image=None, variant=False, pointer=''):
        nonlocal changed
        values = fields(node)
        for category in values.get(keys['category'], {}).get('items', []):
            if text(category):
                categories.add(text(category))
        flag = text(values.get(keys['inherit_icon'], {}))
        inherit = flag.casefold() == 'yes' if flag is not None else settings.options['missing_inherit_icon']
        icon = text(values.get(keys['icon'], {})) or name
        if not icon:
            raise BuildError('image_identity', 'Image reference has no technology or variant identity')
        identifier = base_image if variant and inherit else images.get(
            f'{settings.options["technology_directory"]}/{icon}{settings.options["extension"]}',
            {'technology': current_id, 'representation': name, 'source_ref': {
                'database': 'technologies', 'document_id': document['document_id'], 'pointer': pointer}})
        presentation = {'format_version': 1, 'icon_asset_id': identifier}
        enriched = node.setdefault('enrichments', {})
        if enriched.get('presentation') != presentation:
            enriched['presentation'] = presentation
            changed = True
        return identifier

    for index, node in enumerate(document['items']):
        if node.get('kind') != 'assignment' or node.get('value', {}).get('kind') != 'block':
            continue
        current_id = text(node['key'])
        report['counts']['technologies'] += 1
        base = record(node, current_id, pointer=f'/items/{index}')
        for offset, item in enumerate(node['value']['items']):
            if text(item.get('key', {})) != keys['variant']:
                continue
            report['counts']['variants'] += 1
            record(item, text(fields(item).get(keys['name'], {})), base, True,
                   f'/items/{index}/value/items/{offset}')
    return changed

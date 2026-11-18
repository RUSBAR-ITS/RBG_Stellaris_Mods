"""Select identities and configured text targets from expanded documents."""

from fnmatch import fnmatchcase
from pathlib import PurePosixPath

from sttv.common.errors import BuildError
from sttv.common.datasets import definition
from .targets import Target, assignment, one_field, scalar, variants
from .description_targets import child_targets, descriptions


def root_target(node, pointer, name, kind, keys):
    text_key = keys.get('name_prefix', '') + name
    fields = {}
    if keys.get('name_field'):
        explicit = one_field(node, keys['name_field'], pointer, required=False)
        if explicit:
            fields['name'] = explicit[0]
    elif not keys.get('omit_name'):
        fields['name'] = text_key
    if keys['description_suffix'] is not None:
        fields['description'] = text_key + keys['description_suffix']
    base = Target(pointer, node, name, field_keys=fields, kind=kind)
    if keys['fallback_field']:
        shared = one_field(node, keys['fallback_field'], pointer, required=False)
        if shared:
            base.fallback = (shared[0] + keys['description_suffix'], shared[1])
    return base


def select_targets(database, settings, counts=None, *, document_offset=0, identities=None):
    options, targets = settings.options, []
    identities = {} if identities is None else identities
    directory = PurePosixPath(settings.selection_directory)
    keys, kind = options['keys'], options['kind']
    spec = definition(kind)
    for index, document in enumerate(database['documents'], start=document_offset):
        path = PurePosixPath(document['source']['file'])
        try:
            relative = path.relative_to(directory)
        except ValueError:
            continue
        if (not options['selection']['recursive'] and len(relative.parts) != 1
                or not fnmatchcase(path.name, options['selection']['pattern'])):
            continue
        for number, node in enumerate(document['items']):
            if not assignment(node) or node['value']['kind'] != 'block':
                continue
            if spec['rootTypes'] and node['key']['text'] not in spec['rootTypes']:
                continue
            pointer = f'/documents/{index}/items/{number}'
            if counts is not None:
                counts['objects'] += 1
            name = (one_field(node, spec['idField'], pointer)[0] if spec['identity'] == 'field'
                    else scalar(node['key'], pointer))
            if spec['identity'] not in ('anonymous', 'fragments'):
                if name in identities:
                    raise BuildError('duplicate_object', f'Duplicate {kind} ID: {name}; first definition: {identities[name]}', field_path=pointer)
                identities[name] = pointer
            base = root_target(node, pointer, name, kind, keys)
            nested = []
            if keys['variant']:
                nested.extend(variants(base, keys))
            if keys['description_field']:
                nested.extend(descriptions(base, keys))
            nested.extend(child_targets(base, keys))
            if base.field_keys:
                targets.append(base)
            targets.extend(nested)
    if counts is not None:
        counts['targets'] += len(targets)
    return targets

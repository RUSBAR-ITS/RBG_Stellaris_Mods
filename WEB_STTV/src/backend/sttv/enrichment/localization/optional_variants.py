"""Preserve named conditional presentations without choosing active variants."""

from .targets import entries, one_field
from .description_targets import descriptions


def select_variants(base, keys):
    from .selection import root_target
    for field in keys.get('optional_variants', []):
        for index, node in entries(base.node, field):
            if node['value']['kind'] != 'block':
                continue
            path = f'{base.path}/value/items/{index}'
            explicit = one_field(node, keys['name'], path, required=False)
            # Anonymous variants can have explicit descriptions, but no invented name.
            variant_keys = {**keys, 'omit_name': not bool(explicit),
                            'description_suffix': keys['description_suffix'] if explicit else None}
            target = root_target(node, path, explicit[0] if explicit else base.key, 'variants', variant_keys)
            if target.field_keys:
                yield target
            for description in keys.get('description_fields', []):
                yield from descriptions(target, {**keys, 'description_field': description})

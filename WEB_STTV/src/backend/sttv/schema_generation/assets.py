"""Contracts for prepared card resources and presentation references."""

from .helpers import HASH, TEXT, NULL, BOOL, LINE, RELATIVE, obj, mapping, union, array
from .configuration import selection
from . import localization


def configuration():
    return obj({'format_version': {'const': 1}, 'storage': selection(), 'localization': selection(),
        'source_root': TEXT, 'technology_directory': RELATIVE, 'extension': {'const': '.dds'},
        'dlc_thumbnails': obj({'directory_variable': TEXT, 'field': TEXT}),
        'fields': obj({k: TEXT for k in ('icon', 'variant', 'name', 'inherit_icon', 'category')}),
        'missing_inherit_icon': BOOL, 'research_icons': obj({k: RELATIVE for k in ('physics', 'society', 'engineering')}),
        'directory': RELATIVE, 'conversion': obj({'format': {'const': 'PNG'},
            'compress_level': {'type': 'integer', 'minimum': 0, 'maximum': 9}}),
        'reuse': BOOL, 'category_key': TEXT, 'report': RELATIVE})


def reference():
    return obj({'format_version': {'const': 1}, 'icon_asset_id': union(HASH, NULL)})


def report():
    return obj({'status': {'enum': ['success', 'failed']}, 'inputs': array({'type': 'object'}),
        'duplicates': array({'type': 'object'}), 'diagnostics': array({'type': 'object'}),
        'timings': mapping({'type': 'number', 'minimum': 0}), 'counts': mapping({'type': 'integer', 'minimum': 0}),
        'before': HASH, 'after': HASH, 'published': BOOL, 'coverage': {'type': 'object'}},
        required=['status', 'inputs', 'duplicates', 'diagnostics', 'timings', 'counts'])


def manifest():
    descriptor = obj({'path': RELATIVE, 'mime_type': {'const': 'image/png'}, 'file_hash': HASH,
        'byte_size': LINE, 'width': LINE, 'height': LINE})
    result = obj({'format_version': {'const': 1}, 'revision': HASH, 'settings_revision': HASH,
        'files': mapping(descriptor, HASH),
        'sources': mapping(obj({'source_hash': HASH, 'asset_id': HASH}), RELATIVE),
        'research_icons': obj({k: union(HASH, NULL) for k in ('physics', 'society', 'engineering')}),
        'categories': mapping(obj({k: localization.field() for k in ('ru', 'en')}))})
    result['properties']['dlc_icons'] = mapping(union(HASH, NULL))
    return result

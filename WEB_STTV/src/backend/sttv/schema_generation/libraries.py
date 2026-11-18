"""Closed library settings and whitelisted persistent object records."""

from .helpers import TEXT, STRING, BOOL, HASH, RELATIVE, NULL, obj, array, mapping, union, ref
from sttv.libraries.configuration import KINDS


def configuration():
    return obj({'format_version': {'const': 1}, 'libraries': array(obj({
        'id': TEXT, 'kind': {'enum': list(KINDS)}, 'source': obj({
            'variable': TEXT, 'pattern': TEXT, 'recursive': BOOL, 'encoding': TEXT}), 'output': RELATIVE}), minItems=5, maxItems=5),
        'manifest': RELATIVE, 'report': RELATIVE})


def artifact():
    from sttv.libraries.codec import CLASSES, attributes
    from .library_plan import fields
    value = union(NULL, STRING, BOOL, {'type': 'number'}, array(ref('value')),
                  mapping(ref('value')))
    objects = union(*(obj({'type': {'const': name}, 'fields': obj(fields(cls, attributes(cls)))})
                      for name, cls in CLASSES.items()))
    result = obj({'format': {'const': 'sttv.prepared_library'}, 'format_version': {'const': 1},
                  'preparation_version': TEXT, 'kind': {'enum': list(KINDS)},
                  'graph': obj({'root': ref('value'), 'objects': array(objects)})})
    result['$defs'] = {'value': value}
    return result


def manifest():
    return obj({'format': {'const': 'sttv.library_manifest'}, 'format_version': {'const': 1},
        'preparation_version': TEXT, 'library_set_id': HASH, 'input_fingerprint': HASH,
        'sources': array(obj({'path': TEXT, 'relative': TEXT, 'sha256': HASH, 'kinds': array(TEXT)})),
        'configuration': obj({'sha256': HASH}),
        'artifacts': array(obj({'id': TEXT, 'kind': {'enum': list(KINDS)}, 'path': RELATIVE, 'sha256': HASH}))})


def report():
    return obj({'format': {'const': 'sttv.library_report'}, 'format_version': {'const': 1},
        'mode': {'enum': ['rebuild', 'reuse']}, 'status': {'enum': ['running', 'success', 'failed']},
        'library_set_id': union(HASH, NULL), 'counts': mapping({'type': 'integer', 'minimum': 0}),
        'timings': mapping({'type': 'number', 'minimum': 0}),
        'diagnostics': array(obj({'code': TEXT, 'message': TEXT})), 'bytes': {'type': 'integer', 'minimum': 0}})

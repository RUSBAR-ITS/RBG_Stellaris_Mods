"""Build performance counters without affecting database identity."""

from .helpers import TEXT, array, mapping, obj


def schema():
    from .parallel import performance
    seconds = {'type': 'number', 'minimum': 0}
    count = {'type': 'integer', 'minimum': 0}
    result = obj({'timings': mapping(seconds), 'rule_preparations': count,
                'validated_documents': count,
                'documents': array(obj({'source': TEXT, 'nodes': count,
                    'status': {'enum': ['success', 'failed']}, 'seconds': seconds}))})
    result['properties']['parallel'] = performance()
    return result

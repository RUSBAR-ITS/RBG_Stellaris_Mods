"""Canonical revisions separate source identities from derived combinations."""

import hashlib
import json


IMPLEMENTATION_REVISION = '1.3.0'


def digest(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def script_nodes(node):
    stack = [node]
    while stack:
        item = stack.pop()
        if not isinstance(item, dict) or 'kind' not in item:
            continue
        yield item
        stack.extend(item.get('items', []))
        for key in ('value', 'body', 'block', 'key', 'name', 'tag'):
            child = item.get(key)
            if isinstance(child, dict):
                stack.append(child)


def parameters(settings, technologies):
    result = {'mode': settings.combination['mode'], 'profile': settings.facts,
            'variants': {key: technologies[key]['variant'] for key in sorted(technologies)}}
    if settings.dlc_profile is not None:
        result['dlc'] = settings.dlc_profile
    return result


def rules_revision(metadata):
    value = metadata['rules_snapshot']
    if 'dlc_rules_snapshot' in metadata:
        value = {'parents': value, 'dlc': metadata['dlc_rules_snapshot']}
    return digest(value)


def calculation_revision(metadata):
    return digest({key: metadata[key] for key in ('input_revision', 'rules_revision',
                                                  'parameters_revision', 'implementation_revision')})


def result_revision(metadata, results):
    return digest({'calculation_revision': metadata['calculation_revision'], 'results': results})


def metadata(settings, technologies, set_id, inputs):
    params = parameters(settings, technologies)
    result = {'mode': settings.combination['mode'], 'parameters': params, 'source_set_id': set_id,
        'inputs': sorted(inputs, key=lambda row: row['kind']), 'rules_snapshot': settings.rules,
        'rules_revision': digest(settings.rules), 'parameters_revision': digest(params),
        'implementation_revision': IMPLEMENTATION_REVISION}
    result['input_revision'] = digest({'source_set_id': set_id, 'inputs': result['inputs']})
    if settings.dlc_profile is not None:
        result['dlc_rules_snapshot'] = settings.dlc_rules
        result['rules_revision'] = rules_revision(result)
    result['calculation_revision'] = calculation_revision(result)
    return result

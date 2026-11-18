"""Aggregate job deltas and check cross-document identities deterministically."""

import json

from sttv.common.errors import BuildError
from sttv.common.report import Report


def add_counts(target, value, baseline=None):
    baseline = baseline or {}
    for key, child in value.items():
        if isinstance(child, dict):
            add_counts(target.setdefault(key, {}), child, baseline.get(key))
        elif key in ('max_depth', 'max_call_depth'):
            target[key] = max(target.get(key, 0), child)
        else:
            target[key] = target.get(key, 0) + child - baseline.get(key, 0)


def merge_mapping(target, value):
    for key, child in value.items():
        if key in target and target[key] != child:
            raise BuildError('input_changed', f'Conflicting source records: {key}')
        target[key] = child


def unique_rows(rows):
    unique = {json.dumps(row, sort_keys=True, ensure_ascii=False): row for row in rows}
    return [unique[key] for key in sorted(unique)]


def aggregate(results, build_report, loc_report, library_report, parallel):
    target = build_report.data
    source_ids, identities = set(), {}
    for result in results:
        data = result['report']
        seed = result['seed'] or Report().data
        add_counts(target['counts'], data['counts'], seed['counts'])
        target['diagnostics'].extend(data['diagnostics'][len(seed['diagnostics']):])
        target['source_exceptions'].extend(data['source_exceptions'])
        for name in ('sources', 'inline_sources', 'static_variable_sources', 'scripted_effect_sources',
                     'scripted_trigger_sources', 'script_value_sources', 'library_fields'):
            merge_mapping(target[name], data[name])
        metrics = target['performance']
        add_counts(metrics['timings'], data['performance']['timings'])
        metrics['validated_documents'] += data['performance']['validated_documents']
        metrics['documents'].extend(data['performance']['documents'])
        add_counts(library_report['counts'], result['library']['counts'])
        add_counts(library_report['timings'], result['library']['timings'])
        initial = result['initialization']
        if initial:
            parallel['workers'].append(initial)
            metrics['rule_preparations'] += 1
            library_report['counts']['worker_loaded_artifacts'] = (
                library_report['counts'].get('worker_loaded_artifacts', 0) + initial['counts'].get('loaded_artifacts', 0))
            library_report['timings']['worker_load_sum'] = (
                library_report['timings'].get('worker_load_sum', 0) + initial['timings'].get('load', 0))
        if loc_report is not None:
            local = result['localization']
            add_counts(loc_report['counts'], local['counts'])
            for name in ('inputs', 'duplicates', 'selected_sources', 'diagnostics'):
                loc_report[name].extend(local[name])
        if result['status'] != 'success':
            continue
        identity = tuple(result['fragment']['source_identity'])
        if identity in source_ids:
            raise BuildError('duplicate_source', f'Repeated source: {result["source"]}')
        source_ids.add(identity)
        for name, pointer in result['identities'].items():
            if name in identities:
                raise BuildError('duplicate_object', f'Duplicate ID: {name}; first definition: {identities[name]}',
                                 field_path=pointer)
            identities[name] = pointer
    target['counts']['inline_scripts']['template_files'] = len(target['inline_sources'])
    if loc_report is not None:
        for name in ('inputs', 'duplicates', 'selected_sources'):
            loc_report[name] = unique_rows(loc_report[name])
        observed = {}
        for row in loc_report['inputs']:
            merge_mapping(observed, {row['path']: row['sha256']})

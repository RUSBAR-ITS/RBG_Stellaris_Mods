"""Operation diagnostics are separate from persisted object records."""

from collections import Counter


def initial():
    return {'format': 'sttv.technology_tree_report', 'format_version': 1, 'status': 'failed',
        'action': None, 'database_written': False, 'paths': {}, 'combination': None, 'rules': None,
        'revisions': {}, 'counts': {}, 'timings': {}, 'bytes': {}, 'decisions': [], 'diagnostics': [],
        'ambiguities': [], 'file_hashes': {}, 'coverage': {}, 'error': None}


def summarize(report, results, technologies):
    counts = Counter(row['status'] for row in results.values())
    counts.update({'technologies': len(results), 'single_requirement': sum(len(t['parents']) == 1 for t in technologies.values()),
                   'multiple_requirements': sum(len(t['parents']) > 1 for t in technologies.values()), 'cycles': 0})
    for key in ('root', 'resolved', 'ambiguous'):
        counts.setdefault(key, 0)
    for child, row in results.items():
        if row['parent_tech'] is not None:
            parent = technologies[row['parent_tech']]
            current = technologies[child]
            counts['same_tier'] += current['tier'] == parent['tier']
            counts['parent_higher_tier'] += current['tier'] < parent['tier']
            counts['cross_area'] += current['area'] != parent['area']
    report['counts'].update(counts)
    report['ambiguities'] = [{'decision': row, 'combination': report['combination'], 'rules': report['rules'],
        'revisions': report['revisions'], 'field_state': {'window': None, 'scroll': None, 'supplied': False}}
        for row in report['decisions'] if row['status'] == 'ambiguous']
    report['status'] = 'success_with_warnings' if report['diagnostics'] or counts['ambiguous'] else 'success'


def reused_decisions(technologies, results):
    return [{'id': key, 'variant': t['variant'], 'area': t['area'], 'tier': t['tier'], 'category': t['category'],
        'source': t['source'], 'candidates': t['parents'], 'mandatory': t['mandatory'],
        'prerequisites': t['prerequisites'], 'status': results[key]['status'],
        'parent_tech': results[key]['parent_tech'], 'remaining': None,
        'trace': [], 'trace_state': 'not_recalculated'}
        for key, t in sorted(technologies.items())]

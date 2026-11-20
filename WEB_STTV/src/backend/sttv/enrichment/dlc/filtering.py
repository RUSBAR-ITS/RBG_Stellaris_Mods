"""Record DLC visibility independently from source fields and parent status."""

from .analysis import Analysis


def visibility(technology, names, enabled, rules):
    outcomes, diagnostics = prepare({technology['id']: technology}, names, enabled, rules)
    return outcomes[technology['id']], diagnostics


def prepare(technologies, names, enabled, rules):
    return Analysis(technologies, names, rules).evaluate(enabled)


def select(technologies, outcomes):
    return {key: {**tech, 'parents': [p for p in tech['parents'] if outcomes[p]['visible']]}
            for key, tech in technologies.items() if outcomes[key]['visible']}


def attach(results, decisions, technologies, outcomes):
    diagnostics = []
    for key, technology in technologies.items():
        result = results.setdefault(key, {'parent_tech': None, 'children': [], 'status': 'root'})
        result['visibility'] = outcomes[key]
        excluded = [p for p in technology['parents'] if not outcomes[p]['visible']]
        if outcomes[key]['visible'] and technology['parents'] and len(excluded) == len(technology['parents']):
            diagnostics.append({'code': 'no_visible_parent', 'technology': key,
                                'excluded_candidates': excluded, 'prerequisites': technology['prerequisites']})
        row = next((d for d in decisions if d['id'] == key), None)
        if row is None:
            row = {'id': key, 'status': 'root', 'parent_tech': None, 'trace': []}
            decisions.append(row)
        row.update(visibility=outcomes[key], excluded_candidates=excluded, candidates=technology['parents'])
    decisions.sort(key=lambda d: d['id'])
    return diagnostics

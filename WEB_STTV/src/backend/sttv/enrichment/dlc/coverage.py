"""Reachable proof nodes and unsupported observations are separate coverage facts."""


def reachable(nodes, roots, *, stop_objects=False):
    pending, visited = list(roots), set()
    while pending:
        key = pending.pop()
        if key in visited or stop_objects and nodes[key].get('object_ref'):
            continue
        visited.add(key)
        pending.extend(nodes[key]['children'])
    return visited


def indirect(nodes, root):
    return any(nodes[key].get('object_ref') for key in reachable(nodes, [root]))


def coverage(analysis):
    nodes = analysis.graph.nodes
    result = {key: {'name': name, 'direct': [], 'indirect': [], 'affected': [], 'unresolved': []}
              for key, name in analysis.names.items()}
    unresolved = []
    for technology, roots in sorted(analysis.roots.items()):
        entry = [roots['potential'], *roots['weights'], *(n for _, n in roots['sections'])]
        seen = reachable(nodes, entry)
        direct_nodes = reachable(nodes, entry, stop_objects=True)
        for key in sorted(seen):
            node = nodes[key]
            if node.get('unknown') in ('missing_dlc_reference', 'incomplete_provider_domain',
                    'dlc_depth_limit', 'dlc_node_limit', 'unconfirmed_object_availability', 'dlc_reference_type'):
                unresolved.append({'technology': technology, 'node_id': key, 'reason': node['unknown'],
                                   'target': node.get('target'), 'rule': node.get('rule')})
            if node['op'] == 'dlc':
                mode = 'direct' if key in direct_nodes else 'indirect'
                result[node['dlc_id']][mode].append(technology)
                if not analysis.result[technology]['visible']:
                    result[node['dlc_id']]['affected'].append(technology)
            for observation in node.get('observations', []):
                row = {'technology': technology, 'node_id': key, **observation}
                unresolved.append(row)
                if observation.get('dlc_id') in result:
                    result[observation['dlc_id']]['unresolved'].append(row)
    for row in result.values():
        for mode in ('direct', 'indirect', 'affected'):
            row[mode] = sorted(set(row[mode]))
        row['status'] = ('unresolved_paths' if row['unresolved'] else 'dependencies_found'
                         if row['direct'] or row['indirect'] else 'no_dependencies_found_in_studied_scope')
    return {'dlcs': result, 'unresolved_paths': unresolved}

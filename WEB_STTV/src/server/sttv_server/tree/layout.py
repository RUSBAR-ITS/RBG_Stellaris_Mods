"""Assign logical cells independently in each research area and language."""

from .errors import BuildError


def place(nodes, technologies, ranks, config):
    repeat = config['repeatable']
    digits = str.maketrans('', '', config['ignored_id_characters'])
    visible = {key: row for key, row in nodes.items() if row['availability']}
    columns, roots = {}, {}
    for key, row in visible.items():
        tech = technologies[key]
        column = tech['tier']
        if (column == repeat['game_tier'] and tech['levels'] == repeat['levels']
                and (tech['parents'] or not repeat['requires_prerequisite'])):
            column = repeat['display_tier']
        columns[key] = column
        parent = row['parent_tech']
        if parent is None or visible[parent]['area'] != row['area']:
            roots.setdefault(row['area'], []).append(key)
    # Cross-area edges still participate in the cycle check.
    finished = set()
    for key in visible:
        path = set()
        while key is not None and key not in finished:
            if key in path:
                raise BuildError('tree_cycle', f'Parent cycle at {key}')
            path.add(key)
            key = visible[key]['parent_tech']
        finished.update(path)
    for language, rank in ranks.items():
        visited = set()
        for area, area_roots in roots.items():
            occupied = set()
            bottom = -1
            for root in sorted(area_roots, key=lambda k: (config['starting_roots_first'] and not technologies[k]['starting'], rank[k], k)):
                stack = [(root, bottom + 1)]
                while stack:
                    key, minimum = stack.pop()
                    col = columns[key]
                    row = minimum if minimum is not None else bottom + 1
                    while (col, row) in occupied:
                        row += 1
                    if key in visited:
                        raise BuildError('duplicate_node', key)
                    visited.add(key)
                    occupied.add((col, row))
                    visible[key]['location'][language] = [col, row]
                    bottom = max(bottom, row)
                    children = [k for k in visible[key]['children'] if visible[k]['area'] == area]
                    children.sort(key=lambda k: (k.translate(digits) != key.translate(digits), rank[k], k))
                    for i, child in reversed(list(enumerate(children))):
                        stack.append((child, row + int(columns[child] == col) if i == 0 else None))
        if visited != visible.keys():
            raise BuildError('incomplete_layout', 'Some visible technologies have no cell')

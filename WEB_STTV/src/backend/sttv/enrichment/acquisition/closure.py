"""Select acquisition outputs and their callers before compiling condition graphs."""

from collections import defaultdict, deque
from sttv.enrichment.technology_tree.ast import fields, scalar, references, prerequisite
from .extraction import key, walk
from .effects import Effects


def select(records, targets, levels, library, options):
    effects, entries = options['effects'], options['entries']
    grants, callers, activations, definitions = (defaultdict(set) for _ in range(4))
    path_levels, level_paths, technology_refs, level_refs = {}, defaultdict(set), {}, {}
    by_id = {r['record_id']: r for r in records}
    for record in records:
        rid, body = record['record_id'], record['node'].get('value', {})
        definitions[(record['type'], record['id'])].add(rid)
        technology_refs[rid], level_refs[rid] = set(), set()
        for _, node in walk(body):
            name, value = key(node), node.get('value', {})
            if name in effects['commands']:
                rule = effects['commands'][name]
                target = value.get('text') if value.get('kind') == 'scalar' else scalar(value, rule['target'])
                if rule['handler'] in ('random', 'copy_random', 'copy_all'):
                    target = '*'
                grants[Effects.target(target)].add(rid)
            elif name in effects['event_calls']:
                target = value.get('text') if value.get('kind') == 'scalar' else scalar(value, entries['event_id'])
                callers[Effects.target(target)].add(rid)
            elif name in entries['event_lists']:
                for child in value.get('items', []):
                    target = child.get('text') if child.get('kind') == 'scalar' else child.get('value', {}).get('text')
                    if target:
                        callers[Effects.target(target)].add(rid)
            elif name == effects['activation']:
                activations[Effects.target(value.get('text'))].add(rid)
            elif name == 'has_technology' and value.get('text'):
                technology_refs[rid].add(value['text'])
            elif name == entries['crisis_predicate'] and value.get('text'):
                level_refs[rid].add(value['text'])
        if record['type'] == 'crisis_path':
            ordered = [n.get('text') for block in fields(body, entries['crisis_levels']) for n in block.get('items', [])]
            path_levels[rid] = ordered
            for level in ordered:
                level_paths[level].add(rid)
    selected, technology_seen, level_seen = set(), set(), set()
    queue = deque([('technology', t) for t in targets] + [('level', t) for t in levels])
    queue.extend(('record', rid) for rid in grants['*'])
    while queue:
        kind, identifier = queue.popleft()
        if kind == 'technology':
            if identifier in technology_seen:
                continue
            technology_seen.add(identifier)
            queue.extend(('record', r) for r in grants[identifier])
            technology = library.get('technologies', identifier)
            if technology:
                queue.extend(('technology', t) for t in references(prerequisite(technology['body'])))
                for _, node in walk(technology['body']):
                    name, text = key(node), node.get('value', {}).get('text')
                    if name == 'has_technology' and text:
                        queue.append(('technology', text))
                    if name == entries['crisis_predicate'] and text:
                        queue.append(('level', text))
        elif kind == 'level':
            if identifier in level_seen:
                continue
            level_seen.add(identifier)
            queue.extend(('record', r) for r in definitions[('crisis_level', identifier)])
            for path in level_paths[identifier]:
                queue.append(('record', path))
                ordered = path_levels[path]
                queue.extend(('level', level) for level in ordered[:ordered.index(identifier)])
        else:
            if identifier in selected:
                continue
            selected.add(identifier)
            record = by_id[identifier]
            queue.extend(('technology', t) for t in technology_refs[identifier])
            queue.extend(('level', t) for t in level_refs[identifier])
            if record['type'] == 'event':
                queue.extend(('record', r) for r in callers[record['id']] | callers['*'])
            elif record['type'] == 'crisis_level':
                queue.append(('level', record['id']))
            elif record['type'] == 'crisis_path':
                queue.extend(('record', r) for r in activations[record['id']] | activations['*'])
    return [r for r in records if r['record_id'] in selected], technology_seen

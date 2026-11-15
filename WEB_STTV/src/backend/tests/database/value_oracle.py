"""Check unchanged surroundings without invoking calculation expansion as an oracle."""

from sttv.script.nodes import Assignment, Block, Scalar
from sttv.script.parser import parse_text
from sttv.script.serialization import serialize_document, walk_nodes
from sttv.sources.expansion import expansion_context


def clean(value):
    if isinstance(value, dict):
        return {key: clean(child) for key, child in value.items() if key not in ('span', 'origin')}
    if isinstance(value, list):
        return [clean(child) for child in value]
    return value


def collapse(node, calls, syntax):
    if isinstance(node, dict):
        if node.get('kind') == 'script_value':
            raw = calls[node['origin']['expansion_id']]['invocation']['raw']
            parsed = parse_text(raw, syntax)
            assert len(parsed.items) == 1 and isinstance(parsed.items[0], Scalar)
            return clean(serialize_document(parsed)['items'][0])
        return {key: collapse(child, calls, syntax) for key, child in node.items()
                if key not in ('span', 'origin')}
    if isinstance(node, list):
        return [collapse(child, calls, syntax) for child in node]
    return node


def verify_surroundings(settings, selected, database):
    baseline = expansion_context(settings)
    baseline.library.value_options = None
    checked, constants, targets = 0, 0, set()
    for (path, encoding), saved in zip(selected, database['documents']):
        relative = path.relative_to(settings.game).as_posix()
        parsed = parse_text(path.read_text(encoding=encoding), settings.syntax, relative, expansion=baseline)
        baseline.variables.apply(parsed)
        calls = {r['id']: r for r in saved['metadata']['expansions']}
        assert collapse(saved['items'], calls, settings.syntax) == clean(serialize_document(parsed)['items']), relative
        for _, node in walk_nodes(saved['items']):
            if node['kind'] != 'script_value':
                continue
            call = calls[node['origin']['expansion_id']]
            target = call['target']
            targets.add(target['name'])
            checked += 1
            assert call['kind'] == 'script_value'
            if target['name'] == 'tech_weight_likelihood':
                # Literal acceptance fixture read directly from the installed definition.
                original = parse_text((settings.game / target['file']).read_text(encoding='utf-8-sig'),
                                      settings.syntax, target['file'], role='template')
                definition = next(n for n in original.items
                                  if isinstance(n, Assignment) and n.key.text == target['name'])
                assert isinstance(definition.value, Block)
                expected = clean(serialize_document(original)['items'][original.items.index(definition)]['value'])
                assert clean(node['body']) == expected
                assert node['body']['items'][0]['value']['text'] == '1.25'
                constants += 1
    return dict(documents=len(selected), calculation_nodes=checked, constant_bodies=constants,
                targets=sorted(targets), unchanged_surroundings=True,
                oracle='Collapse reference nodes and compare with calculation expansion disabled; direct constant bodies')

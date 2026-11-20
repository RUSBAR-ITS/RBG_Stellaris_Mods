"""Verify selected installed references against explicit structural expectations."""

import json
from hashlib import sha256

from support import PRODUCT_ROOT
from stellaris_parser.script.nodes import Source
from stellaris_parser.script.inlining.text import slice_source
from stellaris_parser.script.parser import parse_source, parse_text
from stellaris_parser.script.serialization import serialize_document, walk_nodes
from sttv.sources.settings import load_settings
from sttv.sources.expansion import expansion_context
from sttv.database.history import validate_history


def audit(*, library_mode):
    settings = load_settings(PRODUCT_ROOT/'global_variables.json', PRODUCT_ROOT/'config/backend.json', dataset='technologies')
    from sttv.libraries.operation import library_operation
    with library_operation(settings, library_mode) as snapshot:
        result = audit_prepared(settings)
        snapshot.inventory.verify()
        return result


def audit_prepared(settings):
    context = expansion_context(settings)
    documents, hashes = [], {}

    def line(relative, number):
        path = settings.game/relative
        data = path.read_bytes()
        hashes[relative] = sha256(data).hexdigest()
        text = data.decode('utf-8-sig')
        lines = text.splitlines(keepends=True)
        start = sum(map(len, lines[:number-1]))
        part = slice_source(Source(text, relative), start, start+len(lines[number-1]))
        doc = parse_source(part, settings.syntax)
        context.expand(doc, settings.syntax)
        context.variables.apply(doc)
        result = serialize_document(doc)
        validate_history(result)
        documents.append(result)
        return result['items'][0]['value']

    outer = line('events/paragon_events_2.txt', 40)
    body = outer['body']['items']
    assert [n['key']['text'] for n in body] == ['base', 'add', 'min', 'divide', 'mult']
    assert body[1]['value']['scope'] == 'event_target:paragon_destroyed_ship'
    ship = body[1]['value']['body']['items']
    assert ship[1]['value']['items'][0]['value']['text'] == 'count_used_naval_cap'
    heart = body[-1]['value']
    assert heart['kind'] == 'script_value' and heart['scope'] is None
    assert heart['body']['items'][0]['value']['text'] == '1'
    assert heart['body']['items'][1]['value']['items'][0]['value']['text'] == '1.5'
    assert heart['body']['items'][1]['value']['items'][1]['key']['text'] == 'prev'

    building = line('common/script_values/04_script_values_machine_age.txt', 38)
    fields = building['body']['items'][0]['value']['items']
    assert fields[0]['value']['text'] == 'num_buildings'
    parameters = fields[1]['value']['items']
    assert [n['value']['text'] for n in parameters] == ['building_augmentation_center', 'no']
    scoped = line('common/script_values/04_script_values_machine_age.txt', 80)
    assert scoped['scope'] == 'owner'

    def synthetic(text):
        doc = parse_text(text, settings.syntax, 'verification/examples.txt', expansion=context)
        context.variables.apply(doc)
        result = serialize_document(doc)
        validate_history(result)
        documents.append(result)
        return result['items'][0]['value']['body']['items']

    default = synthetic('n=value:country_salvage_ships_from_debris_chance')
    explicit = synthetic('n=value:country_salvage_ships_from_debris_chance|BONUS|no|')
    assert default[3]['value']['text'] == '0'
    assert explicit[3]['value']['text'] == 'no'
    conditional = synthetic('n=value:revolt_situation_low_stability_factor')
    enabled = synthetic('n=value:revolt_situation_low_stability_factor|ALTERED_STABILITY|10|')
    assert [n['key']['text'] for n in conditional] == ['base', 'subtract', 'mult']
    assert [n['key']['text'] for n in enabled] == ['base', 'subtract', 'subtract', 'mult']
    assert enabled[2]['value']['text'] == '10'
    assert all(sha256((settings.game/p).read_bytes()).hexdigest() == h for p,h in hashes.items())
    output = settings.work/'stage9'
    (output/'value_examples.json').write_text(json.dumps(documents,ensure_ascii=False,indent=2),encoding='utf-8')
    report = dict(status='success', real_source_fragments=3, synthetic_calls_to_vanilla_definitions=4,
                  documents=len(documents), source_hashes=hashes, sources_unchanged=True,
                  nested_argument=True, scopes=True, defaults=True, conditional_fragments=True,
                  nodes=sum(sum(1 for _ in walk_nodes(d['items'])) for d in documents))
    (output/'value_examples_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    import argparse
    from sttv.libraries.operation import add_mode_arguments
    parser = argparse.ArgumentParser()
    add_mode_arguments(parser)
    audit(library_mode=parser.parse_args().library_mode)

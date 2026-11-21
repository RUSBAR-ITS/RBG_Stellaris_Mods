"""Inventory raw Stellaris reward sites independently of the expanded parser output."""

import argparse
from collections import Counter
from decimal import Decimal
import json
from pathlib import Path
import re
from zipfile import ZipFile


ROOTS = ('common', 'events', 'map', 'prescripted_countries')
COMMANDS = {'add_research_option', 'give_technology', 'add_tech_progress', 'add_random_research_option',
            'copy_techs_from', 'copy_random_tech_from', 'progress_all_researches', 'give_all_technologies'}
COMMAND_PATTERN = re.compile(rb'\b(?:' + b'|'.join(c.encode() for c in sorted(COMMANDS)) + rb')\s*=', re.I)
TOKEN = re.compile(r'#[^\n]*|"(?:\\.|[^"\\])*"|[{}=]|[^\s{}="#]+')


def find_sites(source, raw):
    text = raw.decode('utf-8-sig', errors='replace')
    stack, results = [], []
    previous_start = 0
    line = 1
    pending, key_line, assigned = '', 0, False
    logical_path = source.partition('!')[-1] if '!' in source else source
    for match in TOKEN.finditer(text):
        # Count newlines inside the previous token as well, including quoted descriptions.
        line += text.count('\n', previous_start, match.start())
        previous_start = match.start()
        token = match[0]
        if token.startswith('#'):
            continue
        if token == '=':
            assigned = True
            continue
        if token == '}':
            if stack:
                stack.pop()
        elif assigned or token == '{':
            key = pending.casefold() if assigned else ''
            block = {'key': key}
            if key in COMMANDS:
                scope = [item['key'] for item in stack[1:]]
                result = {'file': source, 'line': key_line, 'command': key, 'scope': scope, 'fields': {},
                          'library': logical_path.startswith(('common/inline_scripts/', 'common/scripted_effects/')),
                          'tooltip_only': any(s in ('effect_tooltip', 'tooltip', 'custom_tooltip') for s in scope)}
                results.append((stack[0] if stack else {}, result))
                block['command'] = result
            if token == '{':
                stack.append(block)
                if 'command' in block:
                    block['command']['syntax'] = 'block'
            else:
                value = token.strip('"')
                if key == 'id' and len(stack) == 1:
                    stack[0]['id'] = value
                if stack and 'command' in stack[-1]:
                    stack[-1]['command']['fields'][key] = value
                if 'command' in block:
                    block['command'].update(syntax='scalar', fields={'target': value})
        else:
            pending, key_line = token.strip('"'), line
            continue
        pending, assigned = '', False
    for root, site in results:
        site['root'] = root.get('id', root.get('key'))
        site['tech'] = site['fields'].get('tech') or site['fields'].get('target')
        yield site


def inventory(game):
    counts, sites = Counter(), []

    def scan(name, raw):
        counts['files'] += 1
        if COMMAND_PATTERN.search(raw):
            counts['inspected'] += 1
            sites.extend(find_sites(name, raw))

    for prefix in (*ROOTS, 'dlc'):
        for path in sorted((game / prefix).rglob('*.txt')):
            scan(path.relative_to(game).as_posix(), path.read_bytes())
    archives = sorted((game / 'dlc').rglob('*.zip'))
    for path in archives:
        with ZipFile(path) as archive:
            for name in sorted(archive.namelist()):
                if name.lower().endswith('.txt') and name.partition('/')[0].lower() in ROOTS:
                    scan(path.relative_to(game).as_posix() + '!' + name, archive.read(name))
    rules = Path(__file__).resolve().parents[1] / 'config/acquisition_rules.json'
    basis = json.loads(rules.read_bytes())['debris']
    definition = (game / basis['file']).read_text(encoding='utf-8-sig')
    values = re.findall(r'^\s*' + re.escape(basis['key']) + r'\s*=\s*([\d.]+)', definition, re.M)
    assert len(values) == 1 and Decimal(values[0]) == Decimal(basis['fraction']), (basis, values)
    return {'scan': counts, 'archives': len(archives), 'sites': sites,
            'debris_define': {**basis, 'observed': values[0]}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = inventory(args.game)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding='utf8')
    print(result['scan'], 'archives:', result['archives'], 'sites:', len(result['sites']))

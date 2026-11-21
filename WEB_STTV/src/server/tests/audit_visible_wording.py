"""Inventory visible fallback wording in bilingual technology-page API captures."""

import argparse
from collections import defaultdict
import gzip
import json
from pathlib import Path
import re


TERMS = {
    'missing_source': ('source_unnamed',),
    'missing_name': ('name_unavailable', 'module_unavailable', 'missing_game_string'),
    'saved_object': ('saved_role', 'saved_target'),
    'unresolved_check': ('unresolved_condition', 'unresolved_operand', 'status_unresolved', 'partial_technical'),
    'generic_operand': ('named_check', 'unnamed_variable', 'flag_empire_pending', 'neutral_caption'),
    'generic_stage': ('source_hidden', 'source_unknown_stage', 'event_script'),
    'generic_option': ('source_unknown_option',),
    'generic_flag': ('unresolved_flag', 'has_country_flag', 'has_global_flag'),
    'observed_flag': ('flag_observed_object', 'flag_observed_galaxy'),
    'campaign_value': ('dynamic_value', 'dynamic_name'),
}

PAGE_ERRORS = {'missing_source', 'missing_name', 'saved_object', 'unresolved_check', 'generic_operand',
               'generic_stage', 'generic_option', 'generic_flag', 'partial_node', 'empty_group'}


def phrases(language):
    folder = Path(__file__).resolve().parents[3] / 'localization' / language
    dictionary = {}
    for file in folder.glob('*.yml'):
        dictionary.update(re.findall(r'^ sttv_tooltip_(\w+):\d*\s+"(.*)"\s*$', file.read_text(encoding='utf-8-sig'), re.M))
    return {category: tuple(filter(None, (dictionary[key].partition('{')[0].casefold() for key in keys)))
            for category, keys in TERMS.items()}


def survey(folder, inventory):
    results = {}
    for lang, language in [('en', 'english'), ('ru', 'russian')]:
        terms = phrases(language)
        pages = defaultdict(set)
        entries = defaultdict(dict)
        for tech in inventory:
            data = json.loads(gzip.decompress((folder / f'{tech}.{lang}.json.gz').read_bytes()))
            assert (data['technology_id'], data['language']) == (tech, lang)

            def record(category, source, operand, text, section):
                pages[category].add(tech)
                address = '/'.join([section, *source, operand])
                row = entries[category].setdefault(address, {'example': text, 'technologies': set()})
                row['technologies'].add(tech)

            def visit(node, section, source):
                if isinstance(node, list):
                    for child in node:
                        visit(child, section, source)
                    return
                source = node.get('source', source)
                ref = node.get('reference', {})
                operand = ref.get('id') or node.get('key', '')
                for caption in [node.get('text', ''), *node.get('summary', ())]:
                    plain = re.sub(r'§[\w!]', '', caption).casefold()
                    for kind, words in terms.items():
                        candidate = plain
                        if kind == 'missing_name':
                            for specific in terms['missing_source']:
                                candidate = candidate.replace(specific, '')
                        if any(w in candidate for w in words):
                            record(kind, source, operand, caption, section)
                if node.get('kind') == 'partial':
                    record('partial_node', source, operand, node['text'], section)
                if node.get('kind') == 'group' and not node.get('children'):
                    record('empty_group', source, operand, node['text'], section)
                for field in ('children', 'operations', 'formula', 'condition'):
                    if field in node:
                        visit(node[field], section, source)

            for field in ('name', 'description'):
                visit({'text': data.get(field) or ''}, field, [])
            for section, nodes in data['sections'].items():
                visit(nodes, section, [])
            for note in data.get('diagnostics', []):
                if note.get('reason') == 'source_named_by_context':
                    record('source_' + note['basis'], note['source'], '', note['basis'], 'diagnostics')
        for group in entries.values():
            for entry in group.values():
                entry['technologies'] = sorted(entry['technologies'])
        results[lang] = {'technologies_checked': len(inventory),
                         'page_counts': {k: len(v) for k, v in pages.items()}, 'findings': entries}
    return results


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('captures', type=Path)
    cli.add_argument('inventory', type=Path)
    cli.add_argument('output', type=Path)
    cli.add_argument('--check', action='store_true', help='Fail on visible placeholders or empty logical groups')
    args = cli.parse_args()
    ids = json.loads(args.inventory.read_bytes())
    audit = survey(args.captures, ids if isinstance(ids, list) else ids['technology_ids'])
    args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=1), encoding='utf8')
    print({lang: group['page_counts'] for lang, group in audit.items()})
    if args.check and any(PAGE_ERRORS.intersection(group['page_counts']) for group in audit.values()):
        raise SystemExit(1)

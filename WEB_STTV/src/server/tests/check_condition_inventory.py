"""Re-render distinct operands from a previous page audit against the current import."""
import argparse
from collections import defaultdict
import gzip
import json
from pathlib import Path

from sttv_loader.connection import database
from sttv_loader.settings import settings
from sttv_server.config import load_config
from sttv_server.database import selected_strings
from sttv_server.progress_content import ProgressContent
from sttv_server.progress_sources import ProgressSources
from sttv_server.tooltip_document import pack, render
from sttv_server.tooltip_labels import Labels


def expressions(folder):
    observed = defaultdict(set)
    for file in folder.glob('*.en.json.gz'):
        page = json.loads(gzip.decompress(file.read_bytes()))
        for issue in page['diagnostics']:
            if issue['reason'] == 'partial_progress_condition':
                expr = json.dumps(issue['expression'], ensure_ascii=False, sort_keys=True)
                observed[expr].add(page['technology_id'])
    return observed


def inventory(db, rules, folder):
    observed = expressions(folder)
    if not observed:
        raise ValueError('The previous audit does not contain condition diagnostics')
    index = ProgressSources.build(db)
    by_key = defaultdict(list)
    prepared = []
    keys = set()
    for source, pages in observed.items():
        expression = json.loads(source)
        labels = Labels(None, rules, db)
        content = ProgressContent(labels, index, None)
        result = content.node(expression, ('research_progress',))
        if result is None:
            raise ValueError('Previously displayed operand disappeared: ' + source)
        doc = pack(labels, {'technology_id': sorted(pages)[0], 'condition': result})
        prepared.append((expression, sorted(pages), doc))
        keys.update(doc['keys'])
    for language in ('ru', 'en'):
        definitions = {}
        def reader(lang, requested):
            missing = set(requested) - definitions.keys()
            if missing:
                values = dict(selected_strings(db.localization, lang, sorted(missing)))
                definitions.update({key:values.get(key) for key in missing})
            return [(key, definitions[key]) for key in requested if definitions[key] is not None]
        reader(language, keys)
        for expression, pages, doc in prepared:
            rendered = render(doc, rules, reader, language, None)
            node = rendered['condition']
            reasons = sorted({issue['reason'] for issue in rendered['diagnostics']})
            key = expression['key']['text'].casefold()
            by_key[key].append({'language': language, 'expression': expression, 'pages': pages,
                                'presentation': node, 'diagnostics': reasons})
    return dict(sorted(by_key.items()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ('loader-config','server-config','previous','report'):
        parser.add_argument('--' + option, type=Path, required=True)
    args = parser.parse_args()
    rules = load_config(args.server_config.resolve())['key_rules']
    with database(settings(args.loader_config.resolve(), 'network')) as db:
        result = inventory(db, rules, args.previous)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    print(len(result), sum(len(items) for items in result.values()) // 2)

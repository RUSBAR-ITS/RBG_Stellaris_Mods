"""Compare both languages of the published corpus against the previous scope audit."""

from collections import defaultdict
import argparse
import gzip
import json
from pathlib import Path
import re

from audit_visible_wording import PAGE_ERRORS, survey


def captions(node):
    if isinstance(node, list):
        for child in node:
            yield from captions(child)
    elif isinstance(node, dict):
        yield node, [s for s in [node.get('text'), *node.get('summary', ())] if isinstance(s, str)]
        for field in ('children', 'operations', 'condition', 'formula'):
            yield from captions(node.get(field))


def inspect(folder, baseline):
    report = {}
    for lang, families in baseline['matched'].items():
        ids = sorted(baseline['names'])
        words = {k: families[k]['examples'][0]['text'].casefold()
                 for k in ('actor', 'exists_leader', 'exists_owner', 'exists_this', 'generic_hidden_header')}
        dictionary = {}
        locale = 'russian' if lang == 'ru' else 'english'
        for file in (Path(__file__).resolve().parents[3] / 'localization' / locale).glob('*.yml'):
            dictionary.update(re.findall(r'^ sttv_tooltip_([\w.]+):\d*\s+"(.*)"\s*$', file.read_text(encoding='utf-8-sig'), re.M))
        series = {'relative_scope': ['root', 'prev', 'from', 'fromfrom', 'fromfromfrom', 'fromfromfromfrom'],
                  'dynamic_label': ['dynamic_name', 'dynamic_value'],
                  'flag_description_by_evidence': ['flag_observed_object', 'flag_observed_galaxy']}
        patterns = {k: [dictionary[v].split('{')[0].casefold() for v in values] for k, values in series.items()}
        matches = defaultdict(set)
        residual = defaultdict(lambda: defaultdict(dict))
        for identifier in ids:
            data = json.loads(gzip.decompress((folder / f'{identifier}.{lang}.json.gz').read_bytes()))
            assert (data['language'], data['technology_id']) == (lang, identifier)
            for nodes in [[{'text': data.get(k)} for k in ('name', 'description')], *data['sections'].values()]:
                for node, texts in captions(nodes):
                    direct = {c.get('reference', {}).get('id') for c in node.get('children', ())}
                    if node.get('operator') == 'AND' and {'this', 'bio_ship'} <= direct:
                        matches['exact_bioship_guard'].add(identifier)
                    for text in texts:
                        plain = re.sub(r'§[\w!]', '', text).casefold()
                        for k, term in words.items():
                            if term in plain:
                                matches[k].add(identifier)
                        for k, terms in patterns.items():
                            if any(t in plain for t in terms):
                                matches[k].add(identifier)
                        if re.search(r'[«“"](root|from|prev|this)[»”"]', plain):
                            matches['comparison_raw_role'].add(identifier)
                        if re.search(r'\|\|\||\$[^$\n]+\$|\[[\w.:@]+\.get\w+[^\]]*\]|\{[a-z_]+\}', plain):
                            matches['unresolved_markup'].add(identifier)
            for note in data.get('diagnostics', ()):
                reason = note['reason']
                if reason in ('unresolved_participant', 'flag_meaning_from_setters', 'campaign_localization'):
                    code = note.get('flag') or note.get('id') or note.get('key')
                    item = residual[reason][code].setdefault(identifier, [])
                    address = {k: note[k] for k in ('source', 'object', 'file', 'pointer', 'setters') if k in note}
                    if address not in item:
                        item.append(address)
        report[lang] = {'checked': len(ids), 'families': {
            k: {'before': v['technology_count'], 'after': len(matches[k]), 'remaining_ids': sorted(matches[k]),
                'corrected_ids': sorted(set(v['technology_ids']) - matches[k])} for k, v in families.items()},
            'unresolved_markup': sorted(matches['unresolved_markup']), 'diagnostic_evidence': residual}
    return report


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('captures', type=Path)
    cli.add_argument('baseline', type=Path)
    cli.add_argument('output', type=Path)
    args = cli.parse_args()
    baseline = json.loads(args.baseline.read_bytes())
    result = inspect(args.captures, baseline)
    previous_checks = survey(args.captures, sorted(baseline['names']))
    for lang, data in result.items():
        counts = previous_checks[lang]['page_counts']
        data['previous_checks'] = {k: counts.get(k, 0) for k in sorted(PAGE_ERRORS)}
        print(lang, data['checked'], {k: v['after'] for k, v in data['families'].items()}, data['previous_checks'])
    args.output.write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':')), encoding='utf8')
    if any(any(d['previous_checks'].values()) or d['unresolved_markup'] for d in result.values()):
        raise SystemExit(1)

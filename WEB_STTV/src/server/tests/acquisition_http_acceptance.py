"""Check the published acquisition sections against the independent per-ID survey."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

SECTIONS = ('research_options', 'researched_grants', 'research_progress')


def lookup(base, tech, language, enabled=None):
    body = {'technology_id': tech, 'language': language}
    if enabled is not None:
        body['enabled_dlc'] = enabled
    request = Request(base + '/api/trees/technology-tooltip', json.dumps(body).encode(),
                      {'Content-Type': 'application/json'})
    with urlopen(request, timeout=180) as response:
        data = json.load(response)
    assert data['technology_id'] == tech and data['language'] == language and data['name']
    return data


def verify(base, survey, output):
    audit = json.loads(survey.read_bytes())['technologies']
    with urlopen(Request(base + '/api/trees/research-progress', method='DELETE'), timeout=30) as reset:
        assert json.load(reset)['removed_collections'] == 0
    result = {}
    def check(tech):
        data = lookup(base, tech, 'en')
        counts = {}
        for section in SECTIONS:
            groups = data['sections'].get(section, [])
            expected = {tuple(row['source']) for row in audit[tech].get(section, []) if row['status'] == 'confirmed'}
            named = {tuple(group['source']) for group in groups
                     if any(child.get('method') == 'named' for child in group['children'])}
            assert named == expected, (tech, section, named ^ expected)
            if expected:
                counts[section] = len(expected)
        return tech, counts
    with ThreadPoolExecutor(max_workers=3) as pool:
        for tech, counts in pool.map(check, audit):
            result[tech] = counts
    empty = next(tech for tech, counts in result.items() if not counts)
    for lang in ('ru', 'en'):
        for tech in (empty, 'tech_ordered_retreat', 'tech_trinary_computing', 'tech_mine_living_metal',
                     'tech_thrusters_bio_integration', 'tech_alloy_fossilization', 'tech_cryovault', 'tech_crystal_armor_1'):
            data = lookup(base, tech, lang, [])
            groups = data['sections']
            assert {k for k in SECTIONS if any(child.get('method') == 'named'
                for group in groups.get(k, []) for child in group['children'])} == set(result[tech])
            if tech in ('tech_ordered_retreat', 'tech_trinary_computing'):
                observation = next(g for g in groups['research_options'] if g['source'][1] == 'fircon.10')
                assert ('отключ' if lang == 'ru' else 'disabled') in str(observation)
            if tech == 'tech_mine_living_metal':
                assert set(result[tech]) == set(SECTIONS)
                for section in ('research_options', 'research_progress'):
                    mercury = next(g for g in groups[section] if g['source'][1] == 'distar.150')
                    assert ('+25%' in str(mercury)) == (section == 'research_progress')
    try:
        lookup(base, 'sttv_missing_test_technology', 'ru')
    except HTTPError as error:
        assert error.code == 404 and json.load(error)['error'] == 'technology_not_found'
    else:
        raise AssertionError('Expected an unknown technology')
    summary = {k: sum(k in counts for counts in result.values()) for k in SECTIONS}
    output.write_text(json.dumps({'checked': len(result), 'with_section': summary, 'groups_by_technology': result},
                                 indent=2), encoding='utf-8')
    print(len(result), summary)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('base')
    parser.add_argument('survey', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    verify(args.base, args.survey, args.output)

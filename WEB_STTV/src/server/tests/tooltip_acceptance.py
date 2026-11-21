"""Verify complete technology tooltip responses from the running server."""

import argparse
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def post(url, body, status=200):
    request = Request(url, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
    try:
        response = urlopen(request, timeout=15)
    except HTTPError as error:
        response = error
    with response:
        assert response.status == status, (body, response.status)
        return json.load(response)


def check(url, lang):
    alternatives = ('Исследована одна из технологий:' if lang == 'ru'
                    else 'At least one of these technologies has been researched:')
    def sections(identifier):
        body = post(url, {'technology_id': identifier, 'language': lang})
        assert body['language'] == lang and body['technology_id'] == identifier and body['name']
        return body['sections']

    lances, = sections('tech_energy_lance_1')['prerequisites']
    required, options = lances['children']
    assert lances['operator'] == 'AND' and options['operator'] == 'OR'
    assert required['id'] == 'tech_lasers_4'
    assert required['text'] == ('Исследована технология «§YРентгеновские лазеры§!»' if lang == 'ru'
                                else 'Has researched the technology “§YX-Ray Lasers§!”')
    assert options['text'] == alternatives
    assert [n['text'] for n in options['children']] == (
        ['§YЛинкоры§!', '§YЖала§!'] if lang == 'ru' else ['§YBattleships§!', '§YStingers§!'])
    potential, = sections('tech_neuro_quantum_links')['potential']
    origin, group = potential['children']
    authority, civic = group['children']
    assert potential['operator'] == 'AND' and group['operator'] == 'OR'
    assert [(n['key'], n.get('negated', False)) for n in (origin, authority, civic)] == [
        ('has_origin', True), ('has_authority', True), ('has_civic', False)]
    assert [n['text'] for n in (origin, authority)] == (
        ['У государства нет происхождения «§YДикое сознание§!»',
         'Форма правления государства — не «§YМашинный разум§!»'] if lang == 'ru' else
        ['The empire does not have the origin “§YWilderness§!”',
         'The empire’s form of government is not “§YMachine Intelligence§!”'])

    titans = sections('tech_titans')
    group, = titans['prerequisites']
    assert group['operator'] == 'OR' and [n['id'] for n in group['children']] == ['tech_battleships', 'tech_stinger_growth_2']
    assert ('Апокалипсис' if lang == 'ru' else 'Apocalypse') in titans['potential'][0]['text']
    assert group['children'][0]['text'].startswith('§Y') and group['children'][0]['text'].endswith('§!')
    assert group['text'] == alternatives
    rows = titans['weight_modifier']
    assert [row['operations'][0]['value'] for row in rows] == ['0.1', '10', '2', '3', '4', '1.25']
    assert rows[0]['operations'][0]['text'] == ('×0,1' if lang == 'ru' else '×0.1')
    assert '≤ 100' in rows[0]['condition']['text'] and rows[1]['condition']['key'] == 'any_neighbor_country'
    assert rows[1]['condition']['children'][0]['key'] == 'has_technology'
    mega = sections('tech_mega_engineering')
    group, = mega['prerequisites']
    assert group['operator'] == 'AND'
    left, middle, right = group['children']
    assert (left['operator'], middle['id'], right['operator']) == ('OR', 'tech_zero_point_power', 'OR')
    assert left['text'] == right['text'] == alternatives
    assert group['text'] == ('Выполнены все условия:' if lang == 'ru' else 'All of the following are true:')
    assert mega['weight_modifier'][0]['key'] == 'weight_factor' and mega['weight_modifier'][0]['value'] == '0.25'
    synthetic = sections('tech_synthetic_leaders')
    rules = [m for m in synthetic['weight_modifier'] if m.get('kind') == 'modifier']
    group, = [m['condition'] for m in rules if m['operations'][0].get('value') == '0.33'
              and m['condition'].get('operator') == 'AND'
              and [n.get('key') for n in m['condition']['children']] == ['has_origin', 'has_trait_species']]
    assert group['text'].endswith(':') and all('§Y' in n['text'] for n in group['children'])
    assert any(m['condition'].get('key') == 'has_policy_flag' and 'robots_outlawed' not in m['condition']['text']
               for m in rules)
    assert 'weight_modifier' not in sections('tech_crystal_armor_1')
    def flag_texts(identifier):
        def walk(node):
            if isinstance(node, list):
                for child in node:
                    yield from walk(child)
            elif isinstance(node, dict):
                if node.get('key') in ('has_country_flag', 'has_global_flag'):
                    yield node['text']
                for child in node.values():
                    yield from walk(child)
        return list(walk(sections(identifier)))

    mining = flag_texts('tech_mine_rare_crystals')
    assert any(('Найдены' if lang == 'ru' else 'has discovered') in text and '§Y' in text for text in mining)
    assert any(('убой' if lang == 'ru' else 'culled') in text for text in mining)
    assert any(('финансирование' if lang == 'ru' else 'funding') in text for text in flag_texts('tech_frontier_health'))
    assert any(('скопление' if lang == 'ru' else 'L-Cluster') in text for text in flag_texts('tech_repeatable_lcluster_clue'))
    storm = sections('tech_storm_manipulation')['weight_modifier']
    factors = [n for m in storm for n in m.get('operations', []) if n.get('key') == 'factor']
    formula, = [n['formula'] for n in factors if 'formula' in n]
    assert [n['key'] for n in formula] == ['base', 'formula_modifier', 'formula_add']
    multiplication = formula[1]['children'][0]
    assert [n['key'] for n in multiplication['formula']] == ['base', 'add_councilor_level', 'add_councilor_level']
    assert any(n.get('value') == '0' for n in factors)
    archivism = sections('tech_galactic_archivism')['weight_modifier'][0]['operations'][0]
    assert archivism['trigger'] == 'acquired_specimen_count'
    assert ('экземпляров' if lang == 'ru' else 'specimens') in archivism['text']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    url = parser.parse_args().url
    for language in ('ru', 'en'):
        check(url, language)
    assert post(url, {'technology_id': 'sttv_unknown_technology', 'language': 'en'}, 404)['error'] == 'technology_not_found'
    for invalid in ({}, {'technology_id': ['tech_titans'], 'language': 'ru'}, {'technology_id': 'tech_titans', 'language': 'de'}):
        assert post(url, invalid, 400)['error'] == 'invalid_request'
    print('Verified bilingual technology tooltips, flag meanings, missing IDs and malformed requests.')

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
    def sections(identifier):
        body = post(url, {'technology_id': identifier, 'language': lang})
        assert body['language'] == lang and body['technology_id'] == identifier and body['name']
        return body['sections']

    titans = sections('tech_titans')
    group, = titans['prerequisites']
    assert group['operator'] == 'OR' and [n['id'] for n in group['children']] == ['tech_battleships', 'tech_stinger_growth_2']
    assert ('Апокалипсис' if lang == 'ru' else 'Apocalypse') in titans['potential'][0]['text']
    rows = [m['children'] for m in titans['weight_modifier']]
    assert [row[0]['value'] for row in rows] == ['0.1', '10', '2', '3', '4', '1.25']
    assert '≤ 100' in rows[0][1]['text'] and rows[1][1]['key'] == 'any_neighbor_country'
    assert rows[1][1]['children'][0]['key'] == 'has_technology'
    mega = sections('tech_mega_engineering')
    group, = mega['prerequisites']
    assert group['operator'] == 'AND'
    left, middle, right = group['children']
    assert (left['operator'], middle['id'], right['operator']) == ('OR', 'tech_zero_point_power', 'OR')
    assert mega['weight_modifier'][0]['key'] == 'weight_factor' and mega['weight_modifier'][0]['value'] == '0.25'
    synthetic = sections('tech_synthetic_leaders')
    groups = [m['children'] for m in synthetic['weight_modifier'] if m.get('kind') == 'modifier']
    assert any([n['key'] for n in row] == ['factor', 'has_origin', 'has_trait_species']
               and row[0]['value'] == '0.33' for row in groups)
    assert any(n.get('key') == 'has_policy_flag' and 'robots_outlawed' not in n['text']
               for row in groups for n in row)
    armor, = sections('tech_crystal_armor_1')['weight_modifier']
    addition, flag = armor['children']
    assert '+5' in addition['text'] and 'crystal_armor_1_weight' in flag['text']
    storm = sections('tech_storm_manipulation')['weight_modifier']
    factors = [n for m in storm for n in m.get('children', []) if n.get('key') == 'factor']
    formula, = [n['formula'] for n in factors if 'formula' in n]
    assert [n['key'] for n in formula] == ['base', 'formula_modifier', 'formula_add']
    multiplication = formula[1]['children'][0]
    assert [n['key'] for n in multiplication['formula']] == ['base', 'add_councilor_level', 'add_councilor_level']
    assert any(n.get('value') == '0' for n in factors)
    archivism = sections('tech_galactic_archivism')['weight_modifier'][0]['children'][0]
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
    print('Verified RU and EN tooltips for six technologies, missing IDs and malformed requests.')

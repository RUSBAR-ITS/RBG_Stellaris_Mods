"""Reconcile direct vanilla commands, expanded calls and the bilingual browser capture."""

import argparse
from collections import Counter, defaultdict
from decimal import Decimal
import gzip
import json
from pathlib import Path
import re

from sttv_server.progress_sources import COMMANDS


def read(path):
    return json.loads(path.read_bytes())


def compare_sites(sites, rewards):
    by_definition = defaultdict(list)
    for tech, sections in rewards.items():
        for section, entries in sections.items():
            for entry in entries:
                origin = entry['definition']
                by_definition[tech, section, origin['file'], origin['line']].append(entry)
    results, controls = [], []
    for site in sites:
        tech, command = site['tech'], site['command']
        if command not in COMMANDS or tech not in rewards or site['library'] or site['tooltip_only']:
            continue
        key = tech, COMMANDS[command], site['file'], site['line']
        hits = [hit for hit in by_definition[key] if hit['source'][1] == site['root']]
        if not hits:
            assert site['root'] in ('apoc.101', 'graygoo.32'), key
            controls.append(site)
        if command == 'add_tech_progress' and hits:
            value = site['fields'].get('progress')
            if value and value.replace('.', '', 1).isdigit():
                assert all(Decimal(hit['amount']['text']) == Decimal(value) for hit in hits), key
        results.append({'vanilla': site, 'outcomes': hits})
    assert len(results) == 1084 and len(controls) == 6
    return results


def walk(nodes):
    for node in nodes:
        yield node
        for key in ('children', 'formula', 'operations'):
            yield from walk(node.get(key, ()))
        if node.get('condition'):
            yield from walk([node['condition']])


def wording_dictionary(language):
    directory = Path(__file__).resolve().parents[3] / 'localization' / language
    terms = {}
    for path in directory.glob('*.yml'):
        terms.update(re.findall(r'^\s*sttv_tooltip_(\w+):\d*\s+"(.*)"\s*$', path.read_text(encoding='utf-8-sig'), re.M))
    groups = {
        'flag_caption': ('has_country_flag', 'has_global_flag', 'unresolved_flag'),
        'unknown_operand': ('unresolved_condition', 'unresolved_operand'),
        'saved_scope': ('saved_target',), 'campaign_value': ('dynamic_name', 'dynamic_value'),
        'missing_name': ('name_unavailable', 'module_unavailable', 'source_unnamed', 'missing_game_string'),
        'hidden_stage': ('source_hidden',),
    }
    return {key: [terms[k].partition('{')[0].casefold() for k in keys] for key, keys in groups.items()}


def visible_limits(nodes, sections, dictionary):
    limits, flags = defaultdict(set), defaultdict(set)
    for node in nodes:
        caption = re.sub(r'§[\w!]', '', node.get('text', '')).casefold()
        reference = node.get('reference', {})
        identifier = reference.get('id') or node.get('key') or str(node.get('source', ''))
        for key, phrases in dictionary.items():
            if any(p and p in caption for p in phrases):
                limits[key].add(identifier or caption[:180])
        if reference.get('type', '').endswith('_flag'):
            flags[caption].add(reference['id'])
    for ids in flags.values():
        if len(ids) > 1:
            limits['flag_collision'].update(ids)
    for section in COMMANDS.values():
        captions = defaultdict(set)
        for group in sections.get(section, ()):
            captions[group['text']].add('/'.join(group['source']))
        for ids in captions.values():
            if len(ids) > 1:
                limits['same_source_title'].update(ids)
    return {k: sorted(v) for k, v in limits.items()}


def check_priority_cases(tech, nodes, sections, debris):
    if tech.startswith('tech_secrets_'):
        outcomes = [n['text'] for n in walk(sections.get('research_progress', [])) if n.get('method') == 'named']
        assert outcomes and set(outcomes) == {'+10%'}, (tech, outcomes)
    elif tech in ('tech_boarding_cables', 'tech_materiality_engine'):
        section, event = (('researched_grants', 'grand_archive.8265') if tech == 'tech_boarding_cables'
                          else ('research_options', 'shroud_forged.30'))
        assert any(g['source'] == ['events', event] for g in sections[section]), tech
    elif tech in ('tech_mining_drone_weapon_1', 'tech_space_cloud_weapon_1', 'tech_extradimensional_weapon_1',
                  'tech_scourge_missile_1', 'tech_swarm_strike_craft_1', 'tech_nanite_repair_system_synth_queen'):
        assert debris, tech
    elif tech == 'tech_torpedoes_1':
        assert not debris, tech
    elif tech == 'tech_akx_worm_3':
        assert {n['technology_link'] for n in nodes if 'technology_link' in n} == {'tech_akx_worm_1', 'tech_akx_worm_2'}
    elif tech == 'tech_subspace_drive':
        civics = {n['reference']['id'] for n in walk(sections['starting_potential']) if n.get('key') == 'has_civic'}
        assert len(civics) == 4 and 'civic_eager_explorers' in civics
    elif tech == 'tech_xeno_linguistics':
        assert any(n.get('key') == 'add' and n.get('value') == '100' for n in nodes)
    elif tech == 'tech_antimatter_power':
        names = {g['text'] for section in COMMANDS.values() for g in sections.get(section, ())
                 if g['source'] in (['events', 'astral_rift.1005'], ['events', 'astral_rift.1006'])}
        assert len(names) == 2


def review(baseline, run):
    reports = run / 'reports'
    audit = read(baseline)
    before = audit['technologies']
    survey = read(reports / 'player-paths.json')
    rewards = survey['technologies']
    assert set(before) == set(rewards) and len(before) == 679
    raw = read(reports / 'vanilla-sites.json')['sites']
    sites = compare_sites(raw, rewards)
    (reports / 'source-comparison.json').write_text(json.dumps(sites, ensure_ascii=False, indent=1), encoding='utf8')
    captures = read(reports / 'release/pages.json')
    assert {(r['id'], r['lang']) for r in captures} == {(t, l) for t in before for l in ('ru', 'en')}
    by_id = {(r['id'], r['lang']): r for r in captures}
    register, coverage, published_pools = {}, Counter(), Counter()
    phrases = {k: wording_dictionary(v) for k,v in [('ru', 'russian'), ('en', 'english')]}
    visible = {'ru': Counter(), 'en': Counter()}
    limits_by_operand = {lang: defaultdict(lambda: defaultdict(list)) for lang in phrases}
    flag_limits = {}
    original_checks = {lang: audit['diagnostic_operands']['unknown_condition'][lang] for lang in phrases}
    repeated_checks = {lang: defaultdict(list) for lang in phrases}
    for tech, original in before.items():
        expected = rewards[tech]
        row = register[tech] = {'definition': original['definition'], 'carrier_evidence': original['debris'],
            'prior_reward_counts': original['script_site_counts'], 'languages': {}}
        for lang in ('ru', 'en'):
            capture = by_id[tech, lang]
            data = json.loads(gzip.decompress((run / 'artifacts/after' / f'{tech}.{lang}.json.gz').read_bytes()))
            sections = data['sections']
            assert data['technology_id'] == tech and data['language'] == lang
            named, pools, debris = {}, [], []
            for section in COMMANDS.values():
                groups = sections.get(section, [])
                wanted = {tuple(h['source']) for h in expected.get(section, ()) if h['status'] == 'confirmed'}
                got = set()
                for group in groups:
                    assert group.get('summary'), (tech, section)
                    source = tuple(group['source'])
                    if source[0] == 'global_ship_designs':
                        debris.append(source[1])
                        assert group['basis']['fraction'] == '0.10'
                    for child in group['children']:
                        if child.get('method') == 'named':
                            got.add(source)
                        elif child.get('method'):
                            pools.append({'source': source, 'method': child['method'], 'address': child['address']})
                            if lang == 'en' and section != 'research_progress':
                                published_pools[child['method'], source, child['address']['pointer']] += 1
                assert got == wanted, (tech, section, got ^ wanted)
                named[section] = sorted(got)
            nodes = [n for part in sections.values() for n in walk(part)]
            check_priority_cases(tech, nodes, sections, debris)
            wording = visible_limits(nodes, sections, phrases[lang])
            visible[lang].update(wording.keys())
            for kind, operands in wording.items():
                for operand in operands:
                    limits_by_operand[lang][kind][operand].append(tech)
            start = bool(sections.get('starting_potential'))
            duplicate = any(n.get('key') == 'conflicting_weights' for n in nodes)
            assert start == original['definition']['starting_potential']
            assert duplicate == (len(original['definition']['weights']) > 1)
            issues = data['diagnostics']
            issue_ids = defaultdict(set)
            for issue in issues:
                ref = issue.get('flag') or issue.get('id') or issue.get('check') or issue.get('keys') or issue.get('source')
                if ref:
                    issue_ids[issue['reason']].add(str(ref))
            for check in issue_ids.get('unknown_condition', ()):
                if tech in original_checks[lang].get(check, ()):
                    repeated_checks[lang][check].append(tech)
            row['languages'][lang] = {
                'page_ok': capture['ok'], 'page_error': capture.get('error'), 'named': named,
                'debris': debris, 'pool_outcomes': pools, 'conditional_start': start, 'weight_conflict': duplicate,
                'indirect_steps': [n['technology_link'] for n in nodes if n.get('technology_link')],
                'flags_with_sites': [s['flag'] for s in data['flag_evidence']],
                'diagnostics': {key: sorted(values) for key, values in issue_ids.items()},
                'prior_wording': original['pages'][lang]['display_issues'], 'current_wording': wording,
                'reward_deltas': capture.get('changes'),
                'visible_summary_count': capture.get('collapsed'), 'expanded_nodes': len(nodes)}
            if lang == 'ru':
                evidence = {(f['check'], f['flag']): f['sites'] for f in data['flag_evidence']}
                for node in nodes:
                    ref = node.get('reference', {})
                    check, flag = ref.get('type', ''), ref.get('id', '')
                    if not check.endswith('_flag') or not (
                        flag in wording.get('flag_caption', ()) or flag in wording.get('flag_collision', ())
                    ):
                        continue
                    entry = flag_limits.setdefault(check + '=' + flag, {
                        'technologies': set(), 'evidence': {}, 'check': check, 'flag': flag})
                    entry['technologies'].add(tech)
                    for site in evidence.get((check, flag), ()):
                        entry['evidence'][site['file'], site['pointer']] = site
                coverage.update(k for k, active in {'named': any(named.values()), 'debris': debris, 'pools': pools,
                    'conditional_start': start, 'weight_conflict': duplicate, 'missing_flag_label': 'missing_flag_label' in issue_ids,
                    'unknown_condition': bool(issue_ids.get('unknown_condition')),'unknown_scope_role': 'unknown_scope_role' in issue_ids}.items() if active)
    effects = defaultdict(list)
    for cmd, operand, hit in survey['dynamic_calls']:
        origin = hit['definition']
        count = published_pools[cmd, tuple(hit['source']), hit['pointer']]
        domain = {'copy_techs_from': 'donor_knowledge_minus_excluded_technologies',
                  'progress_all_researches': 'research_in_progress_when_effect_runs',
                  'copy_random_tech_from': 'donor_knowledge_and_recipient_eligibility',
                  'add_random_research_option': 'research_options_eligible_at_execution'}[cmd]
        effects[cmd, origin['file'], origin['line']].append({
            **hit, 'operand': operand, 'domain': domain, 'individual_candidates': count,
            'status': hit.get('issue') or ('published_conditional_candidates' if count else 'no_proven_individual_candidate')})
    reviewed = []
    commands = {'add_random_research_option', 'copy_random_tech_from', 'copy_techs_from', 'progress_all_researches'}
    for site in raw:
        cmd = site['command']
        if cmd not in commands:
            continue
        callers = effects[cmd, site['file'], site['line']]
        result_kind = {'copy_techs_from': 'copy_eligible_donor_knowledge',
                       'progress_all_researches': 'advance_current_research',
                       'add_random_research_option': 'research_option'}.get(cmd, 'researched_technology')
        if cmd == 'copy_random_tech_from' and 'progress' in site['fields']:
            result_kind = 'research_option_with_progress'
        if cmd == 'add_random_research_option' and 'add_progress' in site['fields']:
            result_kind = 'research_option_with_progress'
        row = {'site': site, 'outcome': result_kind, 'callers': callers}
        if not callers:
            row['status'] = 'no_executable_call_found_in_snapshot'
        reviewed.append(row)
    assert Counter(r['site']['command'] for r in reviewed) == {
        'add_random_research_option': 79, 'copy_random_tech_from': 14, 'copy_techs_from': 34,
        'progress_all_researches': 1}
    (reports / 'dynamic-sites.json').write_text(json.dumps(reviewed, ensure_ascii=False, indent=1), encoding='utf8')
    (reports / 'wording-limits.json').write_text(json.dumps(limits_by_operand, ensure_ascii=False, indent=1), encoding='utf8')
    for entry in flag_limits.values():
        entry['technologies'] = sorted(entry['technologies'])
        entry['evidence'] = list(entry['evidence'].values())
        entry['limit'] = ('inspect_recorded_setter_and_scope_for_distinct_branch'
                          if any(s['action'].startswith('set_') for s in entry['evidence'])
                          else 'no_setting_operation_for_this_flag_and_scope_in_imported_inputs')
    (reports / 'flag-limits.json').write_text(json.dumps(flag_limits, ensure_ascii=False, indent=1), encoding='utf8')
    zero_weight = {}
    for tech, row in register.items():
        if row['definition']['weights'] != ['0']:
            continue
        displayed = row['languages']['en']
        zero_weight[tech] = [k for k, value in {'named': any(displayed['named'].values()),
            'debris': displayed['debris'], 'starting': row['definition']['starting'],
            'pool': displayed['pool_outcomes']}.items() if value]
    assert len(zero_weight) == 97 and all(zero_weight.values())
    (reports / 'zero-weight.json').write_text(json.dumps(zero_weight, indent=1), encoding='utf8')
    result = {'technologies': len(register), 'pages': len(captures), 'page_failures': sum(not r['ok'] for r in captures),
              'direct_sites': len(sites), 'negative_controls': sum(not r['outcomes'] for r in sites),
              'zero_weight_with_acquisition': len(zero_weight),
              'expanded_outcomes': sum(bool(h['expansion']) for s in rewards.values() for v in s.values() for h in v),
              'dynamic_sites': len(reviewed), 'dynamic_sites_with_calls': sum(bool(r['callers']) for r in reviewed),
              'coverage': dict(coverage), 'expanded_wording': visible, 'recurring_original_checks': repeated_checks}
    (reports / 'register.json').write_text(json.dumps(register, ensure_ascii=False, indent=1), encoding='utf8')
    (reports / 'acceptance.json').write_text(json.dumps(result, indent=2), encoding='utf8')
    print(json.dumps(result))
    assert not result['page_failures']
    assert not coverage['unknown_condition'] and not any(repeated_checks.values()), 'Review remaining condition operands'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    review(args.baseline, args.run)

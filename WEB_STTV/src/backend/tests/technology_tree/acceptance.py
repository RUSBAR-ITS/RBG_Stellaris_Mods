"""Explicit real-data acceptance; expected pairs are read only after calculation."""
from sttv.common.paths import work_directory


import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
from time import perf_counter
from unittest.mock import patch

from sttv.common.json_io import read_json
from sttv.storage import open_set
from sttv.common.paths import PRODUCT_ROOT
from sttv.enrichment.technology_tree import enrich_technology_tree
from sttv.enrichment.technology_tree import evidence
from sttv.enrichment.technology_tree.ast import fields
from sttv.enrichment.technology_tree.inputs import technology_input
from sttv.enrichment.technology_tree.integrity import check_results
from sttv.enrichment.technology_tree.representations import prepare
from sttv.enrichment.technology_tree.revisions import digest
from sttv.enrichment.technology_tree.selection import calculate
from sttv.enrichment.technology_tree.settings import load


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def run(config, reference, expectations, output):
    captured = {}
    original_load = evidence.load
    def capture(*args):
        captured['prepared'] = original_load(*args)
        return captured['prepared']
    print('Calculating base combination and preparing evidence once.', flush=True)
    with patch.object(evidence, 'load', side_effect=capture):
        base = enrich_technology_tree(config_path=config, recalculate=True)
    assert base['status'] == 'success', base['error']
    write(output / 'base_acceptance_report.json', base)
    # The selection module cannot access these comparison files.
    expected = read_json(reference)
    controls = read_json(expectations)['parents']
    actual = {r['id']: (r['parent_tech'], r['status']) for r in base['decisions']}
    previous = {r['id']: (r['parent'], r['status']) for r in expected['decisions']}
    assert actual == previous
    assert all(actual[k][0] == parent for k, parent in controls.items())
    settings = load(config_path=config)
    reader = open_set(settings.storage.manifest)
    before = reader.manifest
    _, records, _ = technology_input(settings, reader)
    selections = [(r['id'], f'swap:{i+1}') for r in records for i in range(len(fields(r['body'], 'technology_swap')))]
    baseline = prepare(records, {})
    changes, rows, totals = [], [], Counter()
    started = perf_counter()
    for key, choice in selections:
        selected = {key: choice}
        technologies = prepare(records, selected)
        results, decisions, diagnostics = calculate(technologies, captured['prepared'], settings.rules, settings.facts)
        check_results(results, technologies)
        reverse = calculate(technologies, captured['prepared'], settings.rules, settings.facts,
                            order=list(reversed(sorted(technologies))))[0]
        assert results == reverse
        if (baseline[key]['area'], baseline[key]['category']) != (technologies[key]['area'], technologies[key]['category']):
            changes.append(selected)
        counts = Counter(r['status'] for r in results.values())
        totals.update(d['code'] for d in diagnostics)
        rows.append({'variants': selected, 'counts': dict(counts), 'diagnostics': diagnostics, 'result_hash': digest(results)})
    multi = {}
    for selection in changes:
        multi.update(selection)
    combinations = [multi, dict(selections[:15]), dict(selections[-15:])]
    for selected in combinations:
        technologies = prepare(records, selected)
        results, _, diagnostics = calculate(technologies, captured['prepared'], settings.rules, settings.facts)
        check_results(results, technologies)
        assert results == calculate(technologies, captured['prepared'], settings.rules, settings.facts)[0]
        rows.append({'variants': selected, 'counts': dict(Counter(r['status'] for r in results.values())),
                     'diagnostics': diagnostics, 'result_hash': digest(results)})
    variant_seconds = perf_counter() - started
    print(f'Checked {len(selections)} individual variants and {len(combinations)} combinations.', flush=True)
    combo = deepcopy(settings.combination)
    combo.update(id='reference_variants', variants=multi)
    combo_path = output / 'variants_combination.json'
    write(combo_path, combo)
    with patch.object(evidence, 'load', return_value=captured['prepared']):
        variant = enrich_technology_tree(config_path=config, combination_path=combo_path)
    assert variant['status'] in ('success','success_with_warnings'), variant['error']
    write(output / 'variant_report.json', variant)
    print('Checking persisted combination reuse.', flush=True)
    with patch.object(evidence, 'load', side_effect=AssertionError('Reuse must not prepare evidence')):
        reused_variant = enrich_technology_tree(config_path=config, combination_path=combo_path)
        reused_base = enrich_technology_tree(config_path=config)
    for reused in (reused_variant, reused_base):
        assert reused['status'] in ('success','success_with_warnings'), reused['error']
        assert reused['action'] == 'reused' and not reused['database_written']
    assert base['revisions'] == reused_base['revisions']
    assert variant['revisions'] == reused_variant['revisions']
    after = open_set(settings.storage.manifest).manifest
    assert all(before['datasets'][k] == after['datasets'][k]
               for k in before['datasets'] if k != 'technologies')
    write(output / 'variant_reuse_report.json', reused_variant)
    write(output / 'base_reuse_report.json', reused_base)
    summary = {'status':'success', 'base_matches':len(actual), 'control_examples':len(controls),
        'variants':len(selections), 'area_category_variants':len(changes), 'combined_checks':len(combinations),
        'variant_seconds':variant_seconds, 'variant_diagnostics':dict(totals),
        'rows':rows, 'base_counts':base['counts'], 'unchanged_other_databases':True,
        'timings':{'forced_base':base['timings'], 'variant_publication':variant['timings'],
                   'base_reuse':reused_base['timings'], 'variant_reuse':reused_variant['timings']}}
    write(output / 'acceptance.json', summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('rows','timings')}, indent=2), flush=True)


if __name__ == '__main__':
    fixtures = PRODUCT_ROOT / 'tests/fixtures/technology_tree'
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--reference', type=Path, default=fixtures / 'report.json')
    parser.add_argument('--expectations', type=Path, default=fixtures / 'expectations.json')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    roots = (work_directory(),)
    if not any(args.output.resolve().is_relative_to(root) for root in roots):
        parser.error('Acceptance artifacts must stay in the product working directory')
    args.output.mkdir(parents=True,exist_ok=True)
    run(args.config,args.reference,args.expectations,args.output)

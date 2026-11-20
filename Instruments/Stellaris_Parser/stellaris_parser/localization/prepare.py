"""Collect every configured definition and prepare an independently loadable package."""

from itertools import batched

from document_package.errors import BuildError
from document_package.package import commit_manifest, confined, save_json, write_batch
from stellaris_parser.localization.index import LocalizationIndex
from stellaris_parser.localization.snapshot import Snapshot


def summarize(index, sources, duplicates):
    counts, winning = {}, {}
    files = {directory: len(paths) for directory, _, paths in index.file_sets}
    for language, tiers in sources.items():
        totals = {'files': 0, 'definitions': 0, 'documents': 0, 'conflicts': 0, 'tiers': {}}
        winners = {}
        for (tier, directory), table in zip(tiers, index.tables[language], strict=True):
            selected = table.keys() - winners.keys()
            winners.update(dict.fromkeys(selected, tier))
            row = {'files': files[directory], 'definitions': sum(map(len, table.values())),
                   'distinct_keys': len(table), 'selected_documents': len(selected), 'conflicts': 0}
            totals['tiers'][tier] = row
            totals['files'] += row['files']
            totals['definitions'] += row['definitions']
        totals['documents'] = len(winners)
        counts[language], winning[language] = totals, winners
    conflicts = []
    for duplicate in duplicates:
        if duplicate['conflicting']:
            language, key, tier = (duplicate[k] for k in ('language', 'key', 'tier'))
            conflicts.append({**duplicate, 'blocking': winning[language][key] == tier})
            counts[language]['conflicts'] += 1
            counts[language]['tiers'][tier]['conflicts'] += 1
    return counts, conflicts, winning


def documents(index, keys):
    for language in sorted(keys):
        for key in sorted(keys[language]):
            definitions = [{**entry['source'], 'raw': entry['raw']}
                           for table in index.tables[language] for entry in table.get(key, ())]
            yield {'_id': {'language': language, 'key': key}, 'selected': 0, 'definitions': definitions}


def prepare(settings, *, save_report=True):
    report = {'status': 'failed', 'languages': {}, 'conflicts': []}
    snapshot = settings.snapshot or Snapshot({'inputs': []})
    path = confined(settings.directory, 'prepare_report.json')
    try:
        sources = settings
        diagnostics = {'duplicates': []}
        index = LocalizationIndex(sources, snapshot, diagnostics)
        counts, conflicts, keys = summarize(index, sources.sources, diagnostics['duplicates'])
        report.update(languages=counts, conflicts=conflicts)
        conflict = next((c for c in conflicts if c['blocking']), None)
        if conflict:
            entries = ', '.join(f"{s['file']}:{s['line']}" for s in conflict['sources'])
            raise BuildError('localization_conflict', f"Conflicting definitions for {conflict['language']} "
                             f"{conflict['key']} in {conflict['tier']}: {entries}")
        batches = [write_batch(settings.directory, batch) for batch in
                   batched(documents(index, keys), settings.options['batch_size'])]
        snapshot.verify()
        index.verify_files()
        commit_manifest(settings.directory, "localization", batches)
        report['status'] = 'success'
        return report
    except (OSError, BuildError, ValueError) as exc:
        report['error'] = str(exc)
        raise
    finally:
        check_report(report)
        if save_report:
            save_json(path, report)


def check_report(report):
    if report['status'] not in ('failed', 'success') or not isinstance(report['languages'], dict):
        raise BuildError('invalid_report', 'Invalid localization preparation report')

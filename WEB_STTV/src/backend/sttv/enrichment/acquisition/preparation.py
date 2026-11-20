"""Prepare immutable per-source indexes with the existing expansion workers."""

from pathlib import Path
from time import perf_counter
from concurrent.futures import as_completed

from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.common.persistence import save_json
from sttv.sources.expansion import source_exclusion
from sttv.sources.files import source_files
from sttv.storage.identity import digest
from sttv.storage.publication import file_digest
from .configuration import REVISION


def inventory(settings, options):
    files = set()
    for directory in options['roots']:
        root = (settings.game / directory).resolve()
        if not root.is_relative_to(settings.game.resolve()) or not root.is_dir():
            raise BuildError('acquisition_source', f'Missing or unsafe acquisition root: {directory}')
        files.update(p for p in source_files(root, options['pattern'], True) if not source_exclusion(p, settings))
    return sorted(files, key=lambda p: p.relative_to(settings.game).as_posix().casefold())


def store(document, output):
    save_json(Path(output), document, 'acquisition_document.schema.json')
    return {'path': str(output), 'source': document['source'], 'file_hash': file_digest(Path(output)),
            'byte_size': Path(output).stat().st_size, 'coverage': document['coverage'],
            'targets': list(document['targets']), 'calls': list(document['calls'])}


def prepare(pool, publication, inputs, options, files):
    started = perf_counter()
    settings = pool.settings
    for file in files:
        inputs.record(file, 'acquisition_source')
    reused = {row['source']: row for row in pool.acquisition_results}
    wanted = {p.relative_to(settings.game).as_posix(): p for p in files}
    missing = [(source, path) for source, path in wanted.items() if source not in reused]
    from .worker import execute
    jobs, rows = {}, [reused[name] for name in wanted if name in reused]
    directory = pool.root / 'acquisition'
    directory.mkdir(exist_ok=True)
    cursor = 0
    # Keep memory bounded by worker count even for several thousand source files.
    while cursor < len(missing) or jobs:
        while cursor < len(missing) and len(jobs) < settings.parallel['workers']:
            source, path = missing[cursor]
            job = {'path': str(path), 'source': source, 'settings': settings, 'options': options,
                   'output': str(directory / f'{cursor}.json')}
            jobs[pool.executor.submit(execute, job)] = source
            cursor += 1
        future = next(as_completed(jobs))
        jobs.pop(future)
        rows.append(future.result())
    descriptors, targets, calls, diagnostics = [], {}, {}, []
    for row in sorted(rows, key=lambda r: r['source'].casefold()):
        source = Path(row.pop('path'))
        path = f'{options["directory"]}/{digest(row["source"])}/{row["file_hash"]}.json'
        publication.accept_auxiliary(source, path, row['file_hash'], row['byte_size'])
        descriptor = {key: row[key] for key in ('source', 'file_hash', 'byte_size', 'coverage')}
        descriptor['path'] = path
        descriptors.append(descriptor)
        for name in row['targets']:
            targets.setdefault(name, []).append(path)
        for name in row['calls']:
            calls.setdefault(name, []).append(path)
        diagnostics.extend(row['coverage']['diagnostics'])
    membership = digest([p.relative_to(settings.game).as_posix() for p in files])
    payload = {'format_version': 1, 'implementation': REVISION, 'context': options['context'],
        'preparation_revision': digest({'library': pool.snapshot.report['library_set_id'],
            'configuration': {str(p): file_digest(p) for p in settings.config_files}}),
        'configuration_revision': options['revision'], 'membership_revision': membership,
        'documents': descriptors, 'targets': targets, 'calls': calls,
        'coverage': {'parsed': not diagnostics, 'diagnostics': diagnostics},
        'statistics': {'reused_documents': len(rows) - len(missing), 'parsed_documents': len(missing),
                       'bytes': sum(d['byte_size'] for d in descriptors), 'seconds': perf_counter() - started}}
    payload['revision'] = digest({k: v for k, v in payload.items() if k != 'statistics'})
    return payload

"""Validate index membership and lazily verify immutable evidence documents."""

from time import perf_counter
from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.common.schema import validate_schema
from sttv.storage.identity import digest, relative
from sttv.storage.settings import confined
from sttv.storage.publication import file_digest
from sttv.storage.reading import signature
from .configuration import REVISION


def empty():
    result = {'format_version': 1, 'implementation': REVISION, 'context': 'playable_empire',
        'configuration_revision': digest(None), 'membership_revision': digest([]), 'documents': [],
        'targets': {}, 'calls': {}, 'coverage': {'parsed': False, 'diagnostics': [{'code': 'acquisition_not_prepared'}]},
        'statistics': {'reused_documents': 0, 'parsed_documents': 0, 'bytes': 0, 'seconds': 0}}
    result['revision'] = digest({k: v for k, v in result.items() if k != 'statistics'})
    return result


def check(index, paths):
    if index['revision'] != digest({k: v for k, v in index.items() if k not in ('revision', 'statistics')}):
        raise BuildError('acquisition_revision', 'Acquisition index revision mismatch')
    sources, declared = set(), set()
    for row in index['documents']:
        path, source = relative(row['path']), relative(row['source']).casefold()
        if path.casefold() in paths or source in sources:
            raise BuildError('acquisition_index', 'Conflicting acquisition document')
        paths.add(path.casefold())
        sources.add(source)
        declared.add(path)
    if any(path not in declared for group in ('targets', 'calls') for paths_ in index[group].values() for path in paths_):
        raise BuildError('acquisition_index', 'Undeclared acquisition target/call document')
    if index['coverage']['parsed'] and any(not r['coverage']['parsed'] and
            r['coverage'].get('classification', {}).get('type') != 'documentation' for r in index['documents']):
        raise BuildError('acquisition_coverage', 'Incomplete input declared complete')


class Index:
    def __init__(self, reader, options):
        self.reader, self.options = reader, options
        self.manifest = reader.manifest['acquisition']
        if self.manifest['implementation'] != REVISION or self.manifest['configuration_revision'] != options['revision']:
            raise BuildError('stale_acquisition', 'Prepare a new set: acquisition index or configuration has changed')
        self.descriptors = {d['path']: d for d in self.manifest['documents']}
        self.records, self.loaded = {}, set()

    def document(self, relative_path):
        row = self.descriptors[relative_path]
        key = ('acquisition', relative_path)
        path = confined(self.reader.root, relative_path)
        if key in self.reader.cache:
            self.reader.check_document(key)
            result = self.reader.cache[key]
        else:
            start, before = perf_counter(), signature(path)
            if path.stat().st_size != row['byte_size'] or file_digest(path) != row['file_hash']:
                raise BuildError('acquisition_hash', f'Acquisition document changed: {relative_path}')
            result = read_json(path)
            validate_schema(result, 'acquisition_document.schema.json')
            if result['source'] != row['source'] or result['coverage'] != row['coverage'] or signature(path) != before:
                raise BuildError('acquisition_document', 'Acquisition source/coverage mismatch')
            for group in ('targets', 'calls'):
                expected = {k for k, rows in self.manifest[group].items() if relative_path in rows}
                if set(result[group]) != expected:
                    raise BuildError('acquisition_index', 'Acquisition target/call inventory mismatch')
            self.reader.paths[key] = path
            self.reader.verified[key] = before
            self.reader.cache[key] = result
            self.reader.bytes += row['byte_size']
            self.reader.seconds += perf_counter() - start
        self.loaded.add(relative_path)
        self.records.update({r['record_id']: r for r in result['records']})
        return result

    def relevant(self, cancelled=None):
        paths = set()
        for group in ('targets', 'calls'):
            paths.update(p for rows in self.manifest[group].values() for p in rows)
        for path in sorted(paths):
            if cancelled is not None and cancelled():
                raise BuildError('cancelled', 'Acquisition index reading cancelled')
            self.document(path)
        return list(self.records.values())

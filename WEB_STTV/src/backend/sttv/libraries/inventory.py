"""Fingerprint library inputs independently of primary documents and localization."""

import hashlib
import json

from sttv.common.errors import BuildError
from sttv.script.inlining.loader import FileTemplates
from sttv.sources.files import source_files

PREPARATION_VERSION = '1'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()


def configuration(settings):
    return {'libraries': [{k: v for k, v in row.items() if k != 'output'}
                         | {'directory': str(row['directory'])} for row in settings.libraries['libraries']],
            'game': str(settings.game), 'lexical': settings.syntax.lexical,
            'constructs': settings.syntax.constructs, 'logical': settings.syntax.logical_operators,
            'inline': settings.inline_options, 'scripted': settings.scripted_options,
            'values': settings.value_options, 'static': settings.static_rules.options,
            'exceptions': settings.parser_exceptions, 'corrections': settings.source_exceptions,
            'preparation_version': PREPARATION_VERSION}


def selected(settings):
    result = {}
    for row in settings.libraries['libraries']:
        directory, options = row['directory'], row['source']
        if not directory.is_dir():
            raise BuildError('source_unavailable', f'Library directory unavailable: {directory}')
        paths = source_files(directory, options['pattern'], options['recursive'])
        if row['kind'] == 'inline_script':
            loader = FileTemplates(directory, settings.inline_options, settings.parser_exceptions['inline_script_files'])
            exceptions = [loader.identity(name)[2] for name in loader.exceptions]
            paths = [*paths, *(path for path in exceptions if path.is_file())]
        for path in sorted(set(paths)):
            path = path.resolve()
            if not path.is_relative_to(directory):
                raise BuildError('unsafe_source', f'Library input escapes its directory: {path}')
            result.setdefault(path, []).append(row['kind'])
    return result


class Inventory:
    def __init__(self, settings, retain=False):
        self.settings, self.raw, self.rows = settings, {}, []
        self.configurations = {path: hashlib.sha256(path.read_bytes()).hexdigest()
                               for path in settings.config_files}
        self.report = None
        self.configuration_hash = digest(configuration(settings))
        physical = {}
        for path, kinds in selected(settings).items():
            try:
                stat = path.stat()
                identity = (stat.st_dev, stat.st_ino)
                if identity not in physical:
                    physical[identity] = path.read_bytes()
                raw = physical[identity]
            except OSError as exc:
                raise BuildError('source_read_error', str(exc)) from exc
            if retain:
                self.raw[path] = raw
            self.rows.append({'path': str(path), 'relative': path.relative_to(settings.game).as_posix(),
                              'sha256': hashlib.sha256(raw).hexdigest(), 'kinds': kinds})
        self.rows.sort(key=lambda row: row['path'].casefold())
        self.reads = len(physical)
        self.fingerprint = digest({'sources': self.rows, 'configuration': self.configuration_hash})

    def reader(self, path, encoding, report, relative, manifest='sources'):
        raw = self.raw[path.resolve()]
        report.data[manifest][relative] = hashlib.sha256(raw).hexdigest()
        try:
            return raw.decode(encoding).replace('\r\n', '\n').replace('\r', '\n')
        except (UnicodeError, LookupError) as exc:
            raise BuildError('source_read_error', str(exc)) from exc

    def verify(self):
        from time import perf_counter
        start = perf_counter()
        current = Inventory(self.settings)
        if self.report is not None:
            counts, timings = self.report['counts'], self.report['timings']
            counts['verification_reads'] = counts.get('verification_reads', 0) + current.reads
            timings['verify_inputs'] = timings.get('verify_inputs', 0) + perf_counter() - start
        if current.fingerprint != self.fingerprint or current.configurations != self.configurations:
            raise BuildError('library_inputs_changed', 'Library inputs changed during the operation')

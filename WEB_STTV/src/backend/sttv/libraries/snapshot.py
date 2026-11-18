"""Immutable prepared contents with fresh counters and call contexts per member."""

from copy import deepcopy

from sttv.common.errors import BuildError
from sttv.common.report import Report
from sttv.script.inlining.loader import FileTemplates
from sttv.script.nodes import Source
from sttv.script.prepared import prepare
from sttv.script.scripted.index import Index
from sttv.script.variables.processor import Processor
from sttv.sources.static_variables import prepare_variables
from sttv.sources.scripted import load_library
from .configuration import reading


class Templates(FileTemplates):
    def __init__(self, settings, sources, checksums, initial=None):
        super().__init__(settings.inline_directory, settings.inline_options,
                         settings.parser_exceptions['inline_script_files'])
        self.sources, self.checksums = sources, checksums
        self.manifest = dict(initial or {})

    def read(self, name):
        _, relative, _ = self.identity(name)
        source = self.sources.get(relative.casefold())
        if source is None:
            raise BuildError('missing_inline_template', f'Missing template: {relative}')
        self.manifest[relative] = self.checksums[relative.casefold()]
        return source


class Snapshot:
    def __init__(self, payloads, inventory, report):
        self.payloads, self.inventory, self.report = payloads, inventory, report
        self.seed = payloads['static_variables']['seed']
        self.shared = payloads['static_variables']['shared']
        for kind, payload in payloads.items():
            count = len(payload['sources']) if kind == 'inline_script' else len(payload)
            if kind == 'static_variables':
                count = len(self.shared)
            report['counts'][f'{kind}_definitions'] = count
            report['counts'][f'{kind}_files'] = sum(kind in row['kinds'] for row in inventory.rows)

    def variables(self, settings, report):
        seed = self.seed
        for key in ('static_variable_sources', 'scripted_effect_sources', 'scripted_trigger_sources',
                    'script_value_sources', 'library_fields', 'diagnostics'):
            report.data[key] = deepcopy(seed[key])
        for key in ('static_variables', 'scripted_calls'):
            report.data['counts'][key] = deepcopy(seed['counts'][key])
        report.data['counts']['warnings'] = seed['counts']['warnings']
        self.report['counts']['contexts'] = self.report['counts'].get('contexts', 0) + 1
        return Processor(settings.static_rules, self.shared, report.data['counts']['static_variables'])

    def context(self, settings, report):
        inline = self.payloads['inline_script']
        templates = Templates(settings, inline['sources'], inline['checksums'], inline['initial_manifest'])
        library = Index(settings.scripted_options)
        library.value_options = settings.value_options
        library.entries = {**self.payloads['scripted_effect'], **self.payloads['scripted_trigger']}
        library.values = self.payloads['script_value']
        library.counts = report.data['counts']['scripted_calls']
        library.file_fields = report.data['library_fields']
        return templates, library


def prepare_snapshot(settings, inventory, report):
    diagnostics = Report()
    variables = prepare_variables(settings, diagnostics, inventory.reader)
    sources, checksums = {}, {}
    for row in inventory.rows:
        if 'inline_script' not in row['kinds']:
            continue
        from pathlib import Path
        path = Path(row['path'])
        relative = path.relative_to(settings.inline_directory).as_posix()
        try:
            text = inventory.raw[path].decode(reading(settings, 'inline_script')['encoding'])
        except (UnicodeError, LookupError) as exc:
            raise BuildError('inline_encoding', f'{relative}: {exc}') from exc
        source = Source(text, relative, 'INLINE_SCRIPTS_DIR')
        sources[relative.casefold()], checksums[relative.casefold()] = source, row['sha256']
    templates = Templates(settings, sources, checksums)
    library = load_library(settings, diagnostics, variables, templates, inventory.reader)
    for source in sources.values():
        prepare(source, settings.syntax)
    payloads = {'inline_script': {'sources': sources, 'checksums': checksums,
                                 'initial_manifest': templates.manifest},
                'scripted_effect': {k: v for k, v in library.entries.items() if v.kind == 'scripted_effect'},
                'scripted_trigger': {k: v for k, v in library.entries.items() if v.kind == 'scripted_trigger'},
                'script_value': library.values,
                'static_variables': {'shared': variables.shared, 'seed': diagnostics.data}}
    report['counts']['prepared_plans'] = len(sources) + len(library.entries) + len(library.values)
    inventory.raw.clear()
    return Snapshot(payloads, inventory, report)

"""Standalone script parsing settings shared by both CLI entry points."""

from dataclasses import asdict
from pathlib import Path

from document_package.json_io import read_json
from document_package.package import confined
from .schema import CONFIG, validate_schema
from .script.source_exceptions import SourceExceptions
from .script.syntax import load_syntax
from .script.values.references import validate_options
from .script.variables.rules import Rules
from .settings import check_output
from .sources import Sources, relative_path

KINDS = ('inline_script', 'scripted_effect', 'scripted_trigger', 'script_value', 'static_variables')


class ScriptSettings:
    def __init__(self, path):
        self.path = Path(path).resolve()
        cfg = read_json(self.path)
        self.config = cfg
        self.sources = Sources([(self.path.parent / root).resolve() for root in cfg['roots']])
        directory = (self.path.parent / cfg.get('syntax_directory', CONFIG)).resolve()
        self.protected = [*self.sources.roots, directory, self.path]
        self.destination = (self.path.parent / cfg['library_directory']).resolve()
        check_output(self.destination, self.protected)
        self.reading = read_json(directory / 'libraries.json')
        self.directories = {kind: relative_path(self.reading[kind]) for kind in KINDS}
        filenames = self.reading['outputs']
        self.outputs = {}
        for kind in (*KINDS, 'manifest'):
            name = relative_path(filenames[kind])
            if len(name.parts) != 1 or name.suffix.lower() != '.json':
                raise ValueError(f'Expected a library JSON filename: {name}')
            self.outputs[kind] = confined(self.destination, name)
        if len(set(self.outputs.values())) != len(self.outputs):
            raise ValueError('Library outputs must use distinct filenames')
        self.syntax = load_syntax(*(directory / f'{k}.json' for k in ('lexical', 'constructs', 'logical_operators')))

        def options(name):
            value = read_json(directory / f'{name}.json')
            validate_schema(value, f'parser_{name}.schema.json')
            return value

        self.rules = Rules(options('static_variables'), self.syntax)
        self.inline = options('inline_scripts')
        self.exceptions = options('exceptions')['inline_script_files']
        self.calls = options('scripted_calls')
        self.values = options('script_values')
        validate_options(self.values, self.syntax)
        self.corrections = options('source_exceptions')

    def source_corrections(self):
        return SourceExceptions(self.corrections, None, 'source_exceptions.json', self.reading['inline_script'])

    def signature(self):
        return {'roots': [str(p) for p in self.sources.roots],
                'reading': {k: v for k, v in self.reading.items() if k != 'outputs'},
                'syntax': asdict(self.syntax), 'static': self.rules.options, 'inline': self.inline,
                'exceptions': self.exceptions, 'calls': self.calls, 'values': self.values,
                'corrections': self.corrections}

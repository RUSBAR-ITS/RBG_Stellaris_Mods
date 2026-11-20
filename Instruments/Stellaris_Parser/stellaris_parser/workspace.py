"""Parse a file using ordered game/mod roots and the shared expansion engine."""

from collections import Counter
from hashlib import sha256
from pathlib import Path

from document_package.errors import BuildError
from document_package.json_io import read_json
from document_package.package import confined
from .schema import ROOT, validate_schema
from .script.inline import Expansion, FileTemplates
from .script.nodes import Source
from .script.parser import parse_text
from .script.scripted.index import Index
from .script.serialization import serialize_document
from .script.source_exceptions import SourceExceptions
from .script.syntax import load_syntax
from .script.values.references import validate_options
from .script.variables.processor import Processor
from .script.variables.rules import Rules
from .script.variables.table import Table
from .settings import check_output


class Sources:
    def __init__(self, config, roots):
        self.roots = roots
        self.options = read_json(config / 'libraries.json')
        if not roots or any(not p.is_dir() for p in roots):
            raise BuildError('missing_root', 'Each configured source root must be an existing directory')

    def find(self, relative):
        for root in self.roots:
            path = confined(root, relative)
            if path.is_file():
                return path
        raise BuildError('source_unavailable', f'Missing source: {relative}')

    def library(self, kind):
        files = {}
        for root in self.roots:
            directory = confined(root, self.options[kind])
            for path in directory.rglob(self.options['pattern']):
                if path.is_file():
                    relative = path.relative_to(root).as_posix()
                    files.setdefault(relative, confined(root, relative))
        for name, path in sorted(files.items()):
            yield name, self.read(path)

    def read(self, path):
        return path.read_text(encoding=self.options['encoding'])


class Templates:
    def __init__(self, sources, options, exceptions):
        self.sources, self.cache, self.manifest = sources, {}, {}
        self.roots = [FileTemplates(confined(root, sources.options['inline_script']), options, exceptions)
                      for root in sources.roots]

    def identity(self, name):
        for root in self.roots:
            key, relative, path = root.identity(name)
            if path.is_file():
                return key, relative, path
        raise BuildError('missing_inline_template', f'Missing inline template: {name}')

    def read(self, name):
        key, relative, path = self.identity(name)
        if key not in self.cache:
            raw = path.read_bytes()
            self.manifest[relative] = sha256(raw).hexdigest()
            self.cache[key] = Source(raw.decode(self.sources.options['encoding']).replace('\r\n', '\n')
                                     .replace('\r', '\n'), relative, 'INLINE_SCRIPTS_DIR')
        return self.cache[key]


def configuration(directory, name):
    options = read_json(directory / f'{name}.json')
    validate_schema(options, f'parser_{name}.schema.json')
    return options


def parse_file(config_path, relative, output):
    config_path = Path(config_path).resolve()
    cfg = read_json(config_path)
    directory = (config_path.parent / cfg.get('syntax_directory', ROOT / 'config')).resolve()
    roots = [(config_path.parent / r).resolve() for r in cfg['roots']]
    check_output(Path(output).resolve(), [*roots, directory, config_path])
    sources = Sources(directory, roots)
    path = sources.find(relative)
    syntax = load_syntax(*(directory / f'{k}.json' for k in ('lexical', 'constructs', 'logical_operators')))
    rules = Rules(configuration(directory, 'static_variables'), syntax)
    table = Table(rules)
    for name, text in sources.library('static_variables'):
        for node in parse_text(text, syntax, name, role='template').items:
            if not rules.declaration(node):
                raise BuildError('invalid_static_library', f'Expected a static declaration in {name}')
            table.add(node)
    variables = Processor(rules, table.resolve_all(), Counter())
    options = configuration(directory, 'inline_scripts')
    templates = Templates(sources, options, configuration(directory, 'exceptions')['inline_script_files'])
    library = Index(configuration(directory, 'scripted_calls'))
    library.value_options = configuration(directory, 'script_values')
    validate_options(library.value_options, syntax)
    corrections = SourceExceptions(configuration(directory, 'source_exceptions'), None,
                                   'source_exceptions.json', sources.options['inline_script'])
    preparer = Expansion(templates, options, variables=variables, exceptions=corrections)
    preparer.preparing = True
    for kind in ('scripted_effect', 'scripted_trigger', 'script_value'):
        for name, text in sources.library(kind):
            document = parse_text(text, syntax, name, role='template')
            preparer.expand(document, syntax, root_only=True)
            object.__setattr__(document, 'node_sources', dict(preparer.sources))
            library.add(document, kind, syntax, variables)
    expansion = Expansion(templates, options, library=library, variables=variables, exceptions=corrections)
    document = parse_text(sources.read(path), syntax, Path(relative).as_posix(), expansion=expansion)
    return serialize_document(variables.apply(document))

"""Parse independent library files, then resolve cross-file definitions in order."""

from collections import Counter
from hashlib import sha256

from document_package.errors import BuildError
from ..scheduling import run_jobs
from ..script.inline import Expansion
from ..script.nodes import Assignment, Block, Document, Source
from ..script.parser import parse_source
from ..script.prepared import prepare
from ..script.scripted.index import Index
from ..script.variables.processor import Processor
from ..script.variables.table import Table
from ..script_settings import KINDS
from .runtime import Templates

_SYNTAX = None
_ENCODING = None
_ROOT_BLOCK_RULES = {}


def initialize(syntax, encoding, rules=()):
    global _SYNTAX, _ENCODING, _ROOT_BLOCK_RULES
    _SYNTAX, _ENCODING = syntax, encoding
    _ROOT_BLOCK_RULES = {}
    for rule in rules:
        if rule['kind'] == 'missing_library_block_separator':
            for path in rule['match']['root_files']:
                _ROOT_BLOCK_RULES.setdefault(path.casefold(), set()).add(rule['match']['field'])


def read_file(job):
    try:
        raw = job.path.read_bytes()
        text = raw.decode(_ENCODING).replace('\r\n', '\n').replace('\r', '\n')
        if job.kind == 'inline_script':
            source = Source(text, job.template, 'INLINE_SCRIPTS_DIR')
            prepare(source, _SYNTAX)
            items = source.plan['items']
        else:
            source = Source(text, job.relative)
            items = parse_source(source, _SYNTAX, root_block_rules=_ROOT_BLOCK_RULES.get(job.relative.casefold())).items
        return job.row(sha256(raw).hexdigest()), {'source': source, 'items': items}
    except (BuildError, ValueError, OSError) as exc:
        # Send a plain exception across the spawn boundary.
        raise ValueError(f'{job.relative}: {exc}') from None


def capture_history(file, document, catalog, index):
    records = document.metadata['expansions']
    file['expansions'] = records
    for record in records:
        position = record['insertion']
        first, size = position['index'], position['count']
        names = [node.key.text for node in document.items[first:first + size]
                 if isinstance(node, Assignment) and isinstance(node.value, Block)]
        record['definitions'] = names
        # A nested include owns its definitions; its parent is recorded on the call.
        for name in names:
            catalog['definition_calls'][index.key(name)] = {'file': document.source.file, 'id': record['id']}


def prepare_libraries(settings, jobs, workers):
    options = (settings.syntax, settings.reading['encoding'], settings.corrections['rules'])
    parsed = dict(run_jobs(jobs, workers, read_file, initialize, options))
    catalogs = {kind: {'files': {}, 'definitions': {}} for kind in KINDS}
    inline = catalogs['inline_script']['definitions']
    table = Table(settings.rules)
    for job in jobs:
        _, file = parsed[job]
        catalogs[job.kind]['files'][job.relative] = file
        if job.kind == 'inline_script':
            key = job.template.casefold()
            if key in inline:
                raise ValueError(f'Ambiguous inline script: {job.template}')
            inline[key] = file['source']
        elif job.kind == 'static_variables':
            for node in file['items']:
                if not settings.rules.declaration(node):
                    raise ValueError(f'Expected a static declaration in {job.relative}')
                table.add(node)

    variables = Processor(settings.rules, table.resolve_all(), Counter())
    catalogs['static_variables']['definitions'] = variables.shared
    templates = Templates(settings, inline)
    index = Index(settings.calls)
    for kind in ('scripted_effect', 'scripted_trigger', 'script_value'):
        catalog = catalogs[kind]
        catalog['definition_calls'] = {}
        for relative, file in catalog['files'].items():
            # Retain the ordered unexpanded nodes even when an include yields no definitions.
            document = Document(file['source'], [], file['items'].copy(), {'expansions': []})
            preparer = Expansion(templates, settings.inline, variables=variables,
                                 exceptions=settings.source_corrections())
            preparer.preparing = True
            preparer.expand(document, settings.syntax, root_only=True)
            object.__setattr__(document, 'node_sources', preparer.sources)
            index.add(document, kind, settings.syntax, variables)
            capture_history(file, document, catalog, index)
        catalog['definitions'] = (index.values if kind == 'script_value' else
                                  {k: v for k, v in index.entries.items() if v.kind == kind})
    return catalogs, [parsed[job][0] for job in jobs]

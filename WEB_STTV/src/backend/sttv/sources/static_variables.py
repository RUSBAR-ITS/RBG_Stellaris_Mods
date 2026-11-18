"""Read the shared variable library once for a build or corpus operation."""

from sttv.script.parser import parse_text
from sttv.script.variables.processor import Processor
from sttv.script.variables.rules import fail
from sttv.script.variables.table import Table
from .files import read_source, source_files


def prepare_variables(settings, report, reader=read_source):
    rules = settings.static_rules
    counts = report.data['counts']['static_variables']
    table, seen = Table(rules), set()
    directory = settings.scripted_variables_directory
    from sttv.libraries.configuration import reading
    options = reading(settings, 'static_variables')
    for path in source_files(directory, options['pattern'], options['recursive']):
        stat = path.stat()
        identity = stat.st_dev, stat.st_ino
        if identity in seen:
            continue
        seen.add(identity)
        relative = path.relative_to(settings.game).as_posix()
        try:
            text = reader(path, options['encoding'], report, relative, 'static_variable_sources')
        finally:
            counts['files'] = len(report.data['static_variable_sources'])
        document = parse_text(text, settings.syntax, relative, role='template')
        for node in document.items:
            if not rules.declaration(node):
                fail('invalid_static_library', 'Only static declarations are allowed in the library', node)
            table.add(node)
            counts['global_definitions'] += 1
    return Processor(rules, table.resolve_all(), counts)


def variable_processor(settings, report):
    from sttv.libraries.operation import current
    return current(settings).variables(settings, report)

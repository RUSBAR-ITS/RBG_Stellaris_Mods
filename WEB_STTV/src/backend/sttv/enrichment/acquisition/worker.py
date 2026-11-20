"""Index additional source files through the same parser and library snapshot."""

from pathlib import Path
from sttv.common.report import Report
from sttv.sources.expansion import expansion_context
from sttv.database.collection import read_document
from .extraction import extract
from .preparation import store


def execute(job):
    from sttv.parallel.worker import STATE
    report, settings = Report(), job['settings']
    classification = job['options'].get('non_executable_sources', {}).get(job['source'])
    if classification:
        from sttv.storage.publication import file_digest
        if file_digest(Path(job['path'])) == classification['sha256']:
            return store({'format': 'sttv.acquisition_document', 'format_version': 1, 'source': job['source'],
                'records': [], 'targets': {}, 'calls': {}, 'coverage': {'parsed': False, 'commands_checked': 0,
                    'diagnostics': [], 'classification': {'type': 'documentation', **classification}}}, job['output'])
    snapshot = STATE['snapshot']
    if STATE['error']:
        from sttv.common.errors import BuildError
        raise BuildError(*STATE['error'])
    variables = snapshot.variables(settings, report)
    expansion = expansion_context(settings, report, variables)
    document = read_document(settings, report, variables, expansion, Path(job['path']), job['options']['encoding'])
    if document is not None:
        result = extract(document, job['options'])
    else:
        result = {'format': 'sttv.acquisition_document', 'format_version': 1, 'source': job['source'],
            'records': [], 'targets': {}, 'calls': {}, 'coverage': {'parsed': False, 'commands_checked': 0,
                'diagnostics': [{'code': 'acquisition_parse_failed', 'source': job['source'],
                                 'details': report.data['diagnostics']}]}}
    return store(result, job['output'])

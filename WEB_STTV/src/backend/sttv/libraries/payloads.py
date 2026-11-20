"""Validate library catalogs and their typed definition references once on load."""

from sttv.common.schema import validate_schema
from stellaris_parser.script.nodes import Source
from stellaris_parser.script.scripted.index import Definition
from stellaris_parser.script.variables.table import Resolved
from .configuration import KINDS
from .references import require


def validate(payloads):
    require(set(payloads) == set(KINDS), 'Incomplete library payload set')
    for kind, payload in payloads.items():
        require(isinstance(payload, dict), f'Invalid {kind} catalog')
        if kind == 'inline_script':
            require(set(payload) == {'sources', 'checksums', 'initial_manifest'}, 'Invalid inline catalog fields')
            sources, checksums = payload['sources'], payload['checksums']
            require(isinstance(sources, dict) and isinstance(checksums, dict) and sources.keys() == checksums.keys(),
                    'Inline sources and checksums differ')
            require(all(isinstance(source, Source) and source.file.casefold() == key for key, source in sources.items()),
                    'Invalid inline source references')
            require(isinstance(payload['initial_manifest'], dict), 'Invalid preparation source manifest')
        elif kind == 'static_variables':
            require(set(payload) == {'shared', 'seed'}, 'Invalid static catalog fields')
            require(isinstance(payload['shared'], dict) and all(isinstance(v, Resolved) for v in payload['shared'].values()),
                    'Invalid static definitions')
            validate_schema(payload['seed'], 'report.schema.json')
        else:
            require(all(isinstance(value, Definition) and value.kind == kind for value in payload.values()),
                    f'Invalid {kind} definition references')

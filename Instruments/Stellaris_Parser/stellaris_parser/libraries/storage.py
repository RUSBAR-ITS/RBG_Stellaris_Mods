"""Publish five prepared graphs and verify the manifest before reusing them."""

from contextlib import contextmanager
from hashlib import file_digest, sha256
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from document_package.errors import BuildError
from document_package.json_io import read_json, unique_object, reject_constant
from document_package.package import save_json
from ..schema import validate_schema
from ..script_settings import KINDS
from .codec import encode, decode
from .inventory import digest, select, source_rows
from .preparation import prepare_libraries

VERSION = '2'
MANIFEST = 'sttv.library_manifest'
ARTIFACT = 'sttv.prepared_library'


@contextmanager
def writer(directory):
    directory.mkdir(parents=True, exist_ok=True)
    if os.name == 'nt':
        try:
            fd = os.open(directory / '.building', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_TEMPORARY)
        except (FileExistsError, PermissionError) as exc:
            raise BuildError('library_busy', f'Cannot acquire library directory: {directory}') from exc
    else:
        import fcntl
        fd = os.open(directory, os.O_RDONLY)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            os.close(fd)
            raise
    try:
        yield
    finally:
        os.close(fd)


def fingerprint(rows, config_hash):
    return digest({'sources': rows, 'configuration': config_hash})


def rebuild(settings, workers):
    with writer(settings.destination):
        catalogs, rows = prepare_libraries(settings, select(settings), workers)
        config_hash = digest(settings.signature())
        with TemporaryDirectory(dir=settings.destination) as stage:
            stage = Path(stage)
            artifacts = []
            for kind in KINDS:
                name = settings.outputs[kind].name
                with (stage / name).open('w', encoding='utf-8', newline='\n') as stream:
                    graph = encode(catalogs[kind])
                    json.dump({'format': ARTIFACT, 'format_version': 1, 'preparation_version': VERSION,
                               'kind': kind, 'graph': graph}, stream, ensure_ascii=False, indent=2, allow_nan=False)
                    stream.write('\n')
                    del graph
                with (stage / name).open('rb') as stream:
                    checksum = file_digest(stream, 'sha256').hexdigest()
                artifacts.append({'id': settings.directories[kind].name, 'kind': kind,
                                  'path': name, 'sha256': checksum})
            if rows != source_rows(select(settings)):
                raise BuildError('library_inputs_changed', 'Library sources changed during preparation')
            manifest = {'format': MANIFEST, 'format_version': 1, 'preparation_version': VERSION,
                        'configuration': {'sha256': config_hash}, 'sources': rows, 'artifacts': artifacts,
                        'input_fingerprint': fingerprint(rows, config_hash),
                        'library_set_id': digest({r['kind']: r['sha256'] for r in artifacts})}
            validate_schema(manifest, 'library_manifest.schema.json')
            save_json(stage / settings.outputs['manifest'].name, manifest)
            for kind in (*KINDS, 'manifest'):
                destination = settings.outputs[kind]
                os.replace(stage / destination.name, destination)
    return catalogs


def load(settings):
    try:
        return _load(settings)
    except (BuildError, OSError, ValueError, KeyError, IndexError, TypeError, AttributeError) as exc:
        raise BuildError('library_reuse_failed', f'{exc}; use --rebuild-libraries') from exc


def _load(settings):
    manifest = read_json(settings.outputs['manifest'])
    validate_schema(manifest, 'library_manifest.schema.json')
    rows = source_rows(select(settings))
    config_hash = digest(settings.signature())
    if (manifest['preparation_version'] != VERSION or manifest['sources'] != rows
            or manifest['configuration']['sha256'] != config_hash
            or manifest['input_fingerprint'] != fingerprint(rows, config_hash)):
        raise ValueError('Library sources, preparation version or settings changed')

    artifacts = manifest['artifacts']
    expected = {(kind, settings.outputs[kind].name) for kind in KINDS}
    if len(artifacts) != len(KINDS) or {(r['kind'], r['path']) for r in artifacts} != expected:
        raise ValueError('Incomplete or mismatched library set')
    if manifest['library_set_id'] != digest({r['kind']: r['sha256'] for r in artifacts}):
        raise ValueError('Library set checksum mismatch')

    catalogs = {}
    for row in artifacts:
        kind = row['kind']
        path = settings.outputs[kind]
        raw = path.read_bytes()
        if sha256(raw).hexdigest() != row['sha256']:
            raise ValueError(f'Library checksum mismatch: {path}')
        value = json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant)
        del raw
        if (value['format'], value['format_version'], value['preparation_version'], value['kind']) != (
                ARTIFACT, 1, VERSION, kind):
            raise ValueError(f'Incompatible library: {path}')
        catalogs[kind] = decode(value['graph'], settings.rules)
        del value
    return catalogs

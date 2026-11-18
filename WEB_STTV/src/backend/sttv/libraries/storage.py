"""Persist complete library snapshots and reject partial or stale generations."""

import hashlib
import json
import os

from sttv.common.errors import BuildError
from sttv.common.paths import output_path
from sttv.common.persistence import prepare_json
from sttv.common.schema import validate_schema
from .codec import encode, decode
from .inventory import PREPARATION_VERSION, digest
from .snapshot import Snapshot
from .validation import artifact_validator


def artifact_hash(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def publish(settings, snapshot):
    pending, artifacts = [], []
    check = artifact_validator()
    try:
        for row in settings.libraries['libraries']:
            destination = output_path(settings.work, row['output'], settings.protected)
            value = {'format': 'sttv.prepared_library', 'format_version': 1,
                     'preparation_version': PREPARATION_VERSION, 'kind': row['kind'],
                     'graph': encode(snapshot.payloads[row['kind']])}
            temporary = prepare_json(destination, value, validator=check)
            pending.append((temporary, destination))
            artifacts.append({'id': row['id'], 'kind': row['kind'], 'path': row['output'],
                              'sha256': artifact_hash(temporary)})
            snapshot.report['bytes'] += temporary.stat().st_size
            snapshot.report['counts'][f'{row["kind"]}_bytes'] = temporary.stat().st_size
        manifest = {'format': 'sttv.library_manifest', 'format_version': 1,
            'preparation_version': PREPARATION_VERSION,
            'library_set_id': digest({row['kind']: row['sha256'] for row in artifacts}),
            'input_fingerprint': snapshot.inventory.fingerprint, 'sources': snapshot.inventory.rows,
            'configuration': {'sha256': snapshot.inventory.configuration_hash}, 'artifacts': artifacts}
        destination = output_path(settings.work, settings.libraries['manifest'], settings.protected)
        pending.append((prepare_json(destination, manifest, 'library_manifest.schema.json'), destination))
        snapshot.inventory.verify()
        for temporary, destination in pending:
            os.replace(temporary, destination)
        snapshot.report['library_set_id'] = manifest['library_set_id']
    finally:
        for temporary, _ in pending:
            temporary.unlink(missing_ok=True)


def load(settings, inventory, report):
    try:
        return load_snapshot(settings, inventory, report)
    except BuildError as exc:
        if '--rebuild-libraries' not in str(exc):
            exc.args = (f'{exc}; use --rebuild-libraries',)
        raise


def check_version(value, expected_format):
    if isinstance(value, dict) and (value.get('format') != expected_format
            or value.get('format_version') != 1 or value.get('preparation_version') != PREPARATION_VERSION):
        raise BuildError('library_version', 'Unsupported library format or preparation version')


def load_snapshot(settings, inventory, report):
    path = output_path(settings.work, settings.libraries['manifest'], settings.protected)
    try:
        manifest = json.loads(path.read_bytes())
    except FileNotFoundError as exc:
        raise BuildError('library_missing', f'Missing snapshot: {path}; use --rebuild-libraries') from exc
    except (ValueError, UnicodeError) as exc:
        raise BuildError('library_corrupt', f'Invalid manifest: {path}; use --rebuild-libraries') from exc
    check_version(manifest, 'sttv.library_manifest')
    validate_schema(manifest, 'library_manifest.schema.json')
    if manifest['preparation_version'] != PREPARATION_VERSION:
        raise BuildError('library_version', 'Preparation version changed; use --rebuild-libraries')
    if manifest['input_fingerprint'] != inventory.fingerprint:
        old = {row['path']: row['sha256'] for row in manifest['sources']}
        now = {row['path']: row['sha256'] for row in inventory.rows}
        changed = sorted(key for key in old.keys() | now.keys() if old.get(key) != now.get(key))
        detail = ', '.join(changed[:12]) or 'Configuration or source selection changed'
        raise BuildError('library_stale', f'{detail}; use --rebuild-libraries')
    expected = {(row['id'], row['kind'], row['output']) for row in settings.libraries['libraries']}
    actual = {(row['id'], row['kind'], row['path']) for row in manifest['artifacts']}
    if expected != actual or len(actual) != len(manifest['artifacts']):
        raise BuildError('library_incomplete', 'Library artifact set differs; use --rebuild-libraries')
    if digest({row['kind']: row['sha256'] for row in manifest['artifacts']}) != manifest['library_set_id']:
        raise BuildError('library_checksum', 'Snapshot identity mismatch; use --rebuild-libraries')
    payloads = {}
    check = artifact_validator()
    for row in manifest['artifacts']:
        path = output_path(settings.work, row['path'], settings.protected)
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise BuildError('library_missing', f'Cannot read {path}; use --rebuild-libraries: {exc}') from exc
        if hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise BuildError('library_checksum', f'Artifact changed: {path}; use --rebuild-libraries')
        try:
            value = json.loads(raw)
        except (ValueError, UnicodeError) as exc:
            raise BuildError('library_corrupt', f'Invalid JSON: {path}; use --rebuild-libraries') from exc
        check_version(value, 'sttv.prepared_library')
        check(value)
        if value['kind'] != row['kind'] or value['preparation_version'] != PREPARATION_VERSION:
            raise BuildError('library_version', f'Artifact version/kind mismatch: {path}')
        payloads[row['kind']] = decode(value['graph'], settings.static_rules)
        report['bytes'] += len(raw)
        report['counts'][f'{row["kind"]}_bytes'] = len(raw)
    report['counts']['loaded_artifacts'] = len(payloads)
    report['library_set_id'] = manifest['library_set_id']
    from .payloads import validate
    validate(payloads)
    return Snapshot(payloads, inventory, report)

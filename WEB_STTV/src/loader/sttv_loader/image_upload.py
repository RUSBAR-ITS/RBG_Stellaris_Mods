"""Prepare selected game images, compare remote hashes and publish changed PNGs."""

import json
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory
from time import perf_counter
from uuid import uuid4

from document_package.errors import BuildError
from document_package.json_io import read_json
from document_package.package import save_json

from .image_receiver import digest
from .image_sources import confined, prepare_png, select_images
from .image_ssh import ssh_receiver


def check_ssh(result, path=None):
    if result.returncode:
        reason = result.stderr.decode('utf-8', errors='replace').strip()
        prefix = f'{path}: ' if path else ''
        raise ValueError(f'{prefix}SSH exited {result.returncode}: {reason}')


def transfer(execute, sources, hashes, artifacts, workspace, counts):
    result = execute('hashes', payload=json.dumps(list(sources)).encode())
    check_ssh(result)
    remote = json.loads(result.stdout)
    if remote.keys() != sources.keys():
        raise ValueError('Incomplete remote hash inventory')
    changed = []
    for name, source in sources.items():
        if hashes[name] == remote[name]:
            counts[source.group]['skipped'] += 1
        else:
            changed.append(name)
    if not changed:
        return

    archive_path = workspace / 'changed.tar'
    with tarfile.open(archive_path, 'w', format=tarfile.PAX_FORMAT) as archive:
        for name in changed:
            with (artifacts / name).open('rb') as stream:
                item = archive.gettarinfo(fileobj=stream, arcname=name)
                item.pax_headers['STTV.sha256'] = hashes[name]
                archive.addfile(item, stream)
    with archive_path.open('rb') as stream:
        result = execute('publish', stream=stream)
    acknowledged = [json.loads(line) for line in result.stdout.splitlines()]
    if acknowledged != changed[:len(acknowledged)]:
        raise ValueError('Unexpected SSH publication acknowledgement')
    for name in acknowledged:
        counts[sources[name].group]['transferred'] += 1
    unconfirmed = changed[len(acknowledged):]
    check_ssh(result, unconfirmed[0] if unconfirmed else None)
    if unconfirmed:
        raise ValueError(f'Unconfirmed upload: {unconfirmed[0]}')


def upload_images(config_path):
    start = perf_counter()
    options = read_json(config_path)
    base = config_path.parent
    game = (base / options['game_root']).resolve()
    descriptors = (base / options['descriptor_directory']).resolve()
    run = (base / options['run_directory']).resolve()
    artifacts = confined(run, run / 'artifacts')
    reports = confined(run, run / 'reports')
    for path in (artifacts, reports):
        for source_root in (game, descriptors):
            if path.is_relative_to(source_root) or source_root.is_relative_to(path):
                raise ValueError(f'Working directory overlaps input: {path}')
    report_path = reports / f'upload-images-{uuid4().hex}.json'
    counts = {name: {'selected': 0, 'transferred': 0, 'skipped': 0} for name in options['groups']}
    report = {'action': 'upload-images', 'destination_root': options['destination_root'],
              'host': options['ssh']['host'], 'groups': counts, 'errors': []}
    try:
        sources = select_images(game, descriptors, options['groups'])
        for source in sources.values():
            counts[source.group]['selected'] += 1
        artifacts.mkdir(parents=True, exist_ok=True)
        hashes = {}
        for name, source in sources.items():
            target = confined(artifacts, artifacts / name)
            prepare_png(source, target)
            with target.open('rb') as stream:
                hashes[name] = digest(stream)
        with TemporaryDirectory(dir=artifacts) as tmp:
            workspace = Path(tmp)
            with ssh_receiver(base, options['ssh'], workspace, report['destination_root']) as execute:
                transfer(execute, sources, hashes, artifacts, workspace, counts)
    except (BuildError, OSError, ValueError, TypeError, KeyError, ImportError, tarfile.TarError) as exc:
        report['errors'].append(str(exc))
        raise BuildError('image_upload', f'{exc} (report: {report_path})') from exc
    finally:
        report['seconds'] = round(perf_counter() - start, 3)
        save_json(report_path, report)
    return {**report, 'report': str(report_path)}

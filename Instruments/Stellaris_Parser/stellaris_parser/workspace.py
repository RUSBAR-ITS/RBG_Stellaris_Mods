"""Single-file and directory operations for the standalone script parser."""

from dataclasses import dataclass
from pathlib import Path
import sys

from document_package.errors import BuildError
from document_package.package import confined, save_json
from .libraries.runtime import Runtime
from .libraries.storage import rebuild, load
from .scheduling import run_jobs
from .script_settings import ScriptSettings
from .settings import check_output
from .sources import SourceFile, relative_path


def runtime_for(settings, mode, workers):
    if mode == 'rebuild':
        catalogs = rebuild(settings, workers)
    elif mode == 'reuse':
        catalogs = load(settings)
    else:
        raise ValueError('Select --rebuild-libraries or --reuse-libraries')
    return Runtime(settings, catalogs)


def parse_file(config_path, relative, output, mode):
    settings = ScriptSettings(config_path)
    check_output(Path(output).resolve(), [*settings.protected, settings.destination])
    relative = relative_path(relative).as_posix()
    path = settings.sources.find(relative)
    return runtime_for(settings, mode, 1).parse(relative, path)


@dataclass(frozen=True)
class ParseJob(SourceFile):
    output: Path


def output_jobs(selected, output):
    owners = {}
    for rel, file in selected.items():
        target = confined(output, rel.with_suffix('.json'))
        if target in owners:
            raise ValueError(f'Conflicting output for {owners[target]} and {rel}: {target}')
        owners[target] = rel
        yield ParseJob(file.relative, file.path, file.size, target)


_WORKER = None


def initialize(runtime):
    global _WORKER
    _WORKER = runtime


def write_file(job):
    try:
        save_json(job.output, _WORKER.parse(job.relative, job.path))
    except (BuildError, ValueError, KeyError, OSError, RecursionError) as exc:
        return f'{job.relative}: {exc}'
    return None


def directory_list(values, allow_root=False):
    if not isinstance(values, list):
        raise ValueError('Expected a list of relative paths')
    return [relative_path(value, allow_root=allow_root) for value in values]


def parse_batch(config_path, mode, directories=None, output=None, workers=None):
    settings = ScriptSettings(config_path)
    return run_batch(settings, mode, directories, output, workers)


def run_batch(settings, mode, directories=None, output=None, workers=None):
    options = settings.config.get('batch', {})
    workers = options.get('workers') if workers is None else workers
    if type(workers) is not int or workers < 1:
        raise ValueError('workers must be a positive integer')
    if output is None:
        output = settings.path.parent / options['output']
    output = Path(output).resolve()
    check_output(output, [*settings.protected, settings.destination])
    excludes = set(directory_list(options.get('exclude_files', [])))
    filters = dict(skip=settings.directories.values(), exclude=excludes)
    if not directories and 'sources' in options:
        patterns = directory_list(options['sources'])
        if not patterns:
            raise ValueError('Select at least one source pattern')
    else:
        directories = directory_list(directories or options.get('directories'), allow_root=True)
        if not directories:
            raise ValueError('Select at least one input directory')
    runtime = runtime_for(settings, mode, workers)
    if directories:
        selected = settings.sources.collect(directories, '*.txt', required=True, **filters)
    else:
        selected = settings.sources.matching(patterns, **filters)
    jobs = list(output_jobs(selected, output))
    failed = 0
    try:
        for _, error in run_jobs(jobs, workers, write_file, initialize, (runtime,)):
            if error is not None:
                print(error, file=sys.stderr)
                failed += 1
    finally:
        initialize(None)
    print(f'Parsed {len(jobs) - failed} of {len(jobs)} files; failed: {failed}')
    return int(bool(failed))

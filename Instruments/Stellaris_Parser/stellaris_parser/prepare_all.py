"""Run the dictionary builder alongside the script parser and its worker pool."""

from multiprocessing import get_context
import sys
from time import perf_counter

from document_package.errors import BuildError
from .localization.prepare import prepare
from .script_settings import ScriptSettings
from .settings import check_output, prepare_settings
from .workspace import run_batch


def write_dictionary(settings):
    started = perf_counter()
    try:
        report = prepare(settings, save_report=False)
    except (BuildError, ValueError, OSError, KeyError) as exc:
        print(f'Localization: {exc}', file=sys.stderr, flush=True)
        raise SystemExit(1) from None
    for language, counts in report['languages'].items():
        print(f"Localization {language}: {counts['files']} files, {counts['documents']} documents", flush=True)
    print(f'Localization ready in {perf_counter() - started:.1f} s', flush=True)


def prepare_all(config_path, mode):
    scripts = ScriptSettings(config_path)
    base = scripts.path.parent
    localization = prepare_settings(scripts.path, base / scripts.config['localization']['output'])
    script_output = (base / scripts.config['batch']['output']).resolve()
    outputs = [script_output, scripts.destination, localization.directory]
    inputs = [*scripts.protected, *(path for tiers in localization.sources.values() for _, path in tiers)]
    for index, output in enumerate(outputs):
        check_output(output, inputs + outputs[:index])

    worker = get_context('spawn').Process(name='localization', target=write_dictionary, args=(localization,))
    worker.start()
    try:
        script_status = run_batch(scripts, mode, output=script_output)
    finally:
        worker.join()
        localization_status = worker.exitcode
        worker.close()
    if localization_status:
        print(f'Localization process exited with status {localization_status}', file=sys.stderr)
    return int(bool(script_status or localization_status))

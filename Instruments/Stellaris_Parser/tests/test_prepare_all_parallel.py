"""Check real spawn lifetimes with file barriers instead of elapsed-time assumptions."""

from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic, sleep
import unittest
from unittest.mock import patch

from stellaris_parser import prepare_all, workspace
from stellaris_parser.localization.reader import read_entries
from stellaris_parser.prepare_all import write_dictionary
from stellaris_parser.workspace import write_file
from test_prepare_all import make_profile


def barrier():
    return Path(os.environ['STELLARIS_PARSER_TEST_BARRIER'])


def wait_for(predicate):
    deadline = monotonic() + 30
    while not predicate():
        if monotonic() > deadline:
            raise TimeoutError(f'Barrier failed; observed {list(barrier().iterdir())}')
        sleep(0.015)


def held_reader(*args):
    for row in read_entries(*args):
        (barrier() / 'reading').touch()
        wait_for((barrier() / 'resume-dictionary').exists)
        yield row


def observed_dictionary(settings):
    # Exclusive creation fails immediately if a second dictionary builder is started.
    with (barrier() / 'dictionary-pid').open('x') as stream:
        stream.write(str(os.getpid()))
    with patch('stellaris_parser.localization.index.read_entries', held_reader):
        write_dictionary(settings)
    (barrier() / 'dictionary-finished').touch()


def held_script(job):
    (barrier() / f'script-{os.getpid()}').touch()
    wait_for((barrier() / 'resume-scripts').exists)
    return write_file(job)


class ParallelPreparationTests(unittest.TestCase):
    def test_dictionary_overlaps_two_script_workers_and_both_are_joined(self):
        with TemporaryDirectory() as name:
            root = Path(name)
            profile = make_profile(root)
            runtime_for = workspace.runtime_for
            run_batch = prepare_all.run_batch

            def wait_at_library_preparation(*args, **kwargs):
                wait_for((barrier() / 'reading').exists)
                return runtime_for(*args, **kwargs)

            def observed_batch(*args, **kwargs):
                status = run_batch(*args, **kwargs)
                (barrier() / 'scripts-finished').touch()
                return status

            for first, last in [('scripts', 'dictionary'), ('dictionary', 'scripts')]:
                gate = root / f'{first}-first'
                gate.mkdir()
                with (self.subTest(first=first),
                      patch.dict(os.environ, STELLARIS_PARSER_TEST_BARRIER=str(gate)),
                      patch.object(prepare_all, 'write_dictionary', observed_dictionary),
                      patch.object(prepare_all, 'run_batch', observed_batch),
                      patch.object(workspace, 'runtime_for', wait_at_library_preparation),
                      patch.object(workspace, 'write_file', held_script),
                      ThreadPoolExecutor(max_workers=1) as caller):
                    result = caller.submit(prepare_all.prepare_all, profile, 'rebuild')
                    try:
                        wait_for(lambda: len(list(gate.glob('script-*'))) == 2)
                        pids = {int(p.name.split('-')[1]) for p in gate.glob('script-*')}
                        self.assertNotIn(int((gate / 'dictionary-pid').read_text()), pids)
                        (gate / f'resume-{first}').touch()
                        wait_for((gate / f'{first}-finished').exists)
                        self.assertFalse((gate / f'{last}-finished').exists())
                        self.assertFalse(result.done())
                    finally:
                        (gate / 'resume-scripts').touch()
                        (gate / 'resume-dictionary').touch()
                    self.assertEqual(result.result(timeout=30), 0)
                    self.assertTrue((gate / f'{last}-finished').is_file())

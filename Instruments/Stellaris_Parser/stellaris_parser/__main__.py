"""Prepare localization or parse game scripts using a reusable library set."""

import argparse
from concurrent.futures.process import BrokenProcessPool
import json
import sys
from pathlib import Path

from document_package.errors import BuildError
from document_package.package import save_json
from .localization.prepare import prepare
from .settings import prepare_settings


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest='action', required=True)
    for name in ('prepare', 'parse', 'parse-batch', 'prepare-all'):
        command = commands.add_parser(name)
        command.add_argument('--config', type=Path, required=True)
        if name != 'prepare-all':
            command.add_argument('--output', type=Path, required=name != 'parse-batch')
        if name != 'prepare':
            modes = command.add_mutually_exclusive_group(required=True)
            for mode in ('rebuild', 'reuse'):
                modes.add_argument(f'--{mode}-libraries', action='store_const', dest='mode', const=mode)
        if name == 'parse':
            command.add_argument('source', help='Path relative to a configured source root')
        if name == 'parse-batch':
            command.add_argument('directories', nargs='*', help='Directories relative to source roots')
            command.add_argument('--workers', type=int, help='Maximum number of worker processes')
    args = cli.parse_args()
    try:
        if args.action == 'prepare':
            report = prepare(prepare_settings(args.config, args.output))
            print(json.dumps(report['languages'], indent=2))
        elif args.action == 'prepare-all':
            from .prepare_all import prepare_all
            return prepare_all(args.config, args.mode)
        elif args.action == 'parse':
            from .workspace import parse_file
            save_json(args.output.resolve(), parse_file(args.config, args.source, args.output, args.mode))
        else:
            from .workspace import parse_batch
            return parse_batch(args.config, args.mode, args.directories, args.output, args.workers)
        return 0
    except (BuildError, ValueError, OSError, KeyError, BrokenProcessPool) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

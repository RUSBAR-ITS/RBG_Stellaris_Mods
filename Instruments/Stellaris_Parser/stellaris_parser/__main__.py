"""Prepare a localization package or parse a selected script."""

import argparse
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
    for name in ('prepare', 'parse'):
        command = commands.add_parser(name)
        command.add_argument('--config', type=Path, required=True)
        command.add_argument('--output', type=Path, required=True)
        if name == 'parse':
            command.add_argument('source', help='Path relative to a configured source root')
    args = cli.parse_args()
    try:
        if args.action == 'prepare':
            report = prepare(prepare_settings(args.config, args.output))
            print(json.dumps(report['languages'], indent=2))
        else:
            from .workspace import parse_file
            save_json(args.output.resolve(), parse_file(args.config, args.source, args.output))
        return 0
    except (BuildError, ValueError, OSError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

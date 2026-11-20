"""Load or verify a prepared document package."""

import argparse
import json
import sys
from pathlib import Path

from pymongo.errors import PyMongoError

from document_package.errors import BuildError
from document_package.package import Package
from sttv.mongo.connection import database
from sttv.mongo.settings import collection_name, settings
from .publication import publish, verify


def run(action, config, package):
    logical = package.manifest['collection']
    if logical not in config.options['collections']:
        raise BuildError('unknown_collection', f'No destination configured for {logical!r}')
    target = collection_name(config.options['collections'][logical])
    if config.scratch.is_relative_to(package.directory):
        raise BuildError('unsafe_scratch', 'Loader scratch must be outside the package')
    with database(config) as db:
        collection = db[target]
        count = (publish if action == 'load' else verify)(collection, package)
        return {'action': action, 'profile': config.name, 'collection': collection.full_name,
                'documents': count}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('action', choices=['load', 'verify'])
    cli.add_argument('--package', required=True, type=Path)
    cli.add_argument('--config', required=True, type=Path)
    cli.add_argument('--profile')
    args = cli.parse_args()
    try:
        print(json.dumps(run(args.action, settings(args.config, args.profile), Package(args.package))))
    except PyMongoError as exc:
        print(f'MongoDB {type(exc).__name__} (code {exc.code if hasattr(exc, "code") else None})', file=sys.stderr)
        return 1
    except (BuildError, OSError, ValueError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

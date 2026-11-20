"""Manage MongoDB and load configured JSON sources."""

import argparse
import json
import sys
from pathlib import Path

from bson.errors import BSONError
from document_package.errors import BuildError
from pymongo.errors import PyMongoError

from .connection import database
from .importer import transfer
from .inputs import Inputs
from .publication import CONTROL, create, staging, writer
from .settings import settings


def collection_versions(db, names):
    if db[CONTROL].find_one({'_id': 'writer'}, {'_id': 1}):
        raise BuildError('loader_busy', 'Database publication is in progress or requires recovery')
    with db.list_collections(filter={'name': {'$in': names}}) as collections:
        versions = {item['name']: item['info']['uuid'] for item in collections}
    missing = set(names) - versions.keys()
    if missing:
        raise BuildError('missing_collection', f'Missing collections: {sorted(missing)}')
    return versions


def run(action, config_path, profile=None):
    config_path = Path(config_path).resolve()
    config = settings(config_path, profile)
    inputs = Inputs(config.options, config_path.parent)
    if any(config.scratch.is_relative_to(source.path) for source in inputs.sources):
        raise BuildError('unsafe_scratch', 'Loader scratch must be outside the input sources')
    counts = {}
    with database(config) as db:
        if db.name in ('admin', 'config', 'local'):
            raise BuildError('system_database', f'Expected an application database, got {db.name}')
        if action == 'verify':
            versions = collection_versions(db, inputs.names)
            counts = transfer(inputs, {n: db[n] for n in inputs.names}, writing=False)
            if collection_versions(db, inputs.names) != versions:
                raise BuildError('publication_changed', 'Collections changed during verification')
        else:
            with writer(db, config.scratch):
                if action == 'create':
                    create(db, inputs.names)
                elif action == 'drop':
                    db.client.drop_database(db.name)
                elif action == 'load':
                    with staging(db, inputs.names) as targets:
                        counts = transfer(inputs, targets, writing=True)
                else:
                    raise ValueError(f'Unknown loader action: {action}')
        return {'action': action, 'profile': config.name, 'database': db.name, 'documents': counts}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('action', choices=('create', 'drop', 'load', 'verify'))
    cli.add_argument('--config', required=True)
    cli.add_argument('--profile')
    args = cli.parse_args()
    try:
        print(json.dumps(run(args.action, args.config, args.profile), ensure_ascii=False))
    except PyMongoError as exc:
        print(f'MongoDB {type(exc).__name__} (code {getattr(exc, "code", None)})', file=sys.stderr)
        return 1
    except (BSONError, BuildError, OSError, ValueError, TypeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

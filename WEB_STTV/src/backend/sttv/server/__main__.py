"""Run the MongoDB localization reader or serve it over HTTP."""

import argparse
import json
import sys

from pymongo.errors import PyMongoError
from document_package.errors import BuildError
from sttv.mongo.connection import database
from sttv.mongo.settings import collection_name, settings
from .http import lookup, make_server


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--config', required=True)
    cli.add_argument('--profile')
    commands = cli.add_subparsers(dest='action', required=True)
    read = commands.add_parser('read')
    read.add_argument('language')
    read.add_argument('key')
    commands.add_parser('serve')
    args = cli.parse_args()
    try:
        config = settings(args.config, args.profile)
        with database(config) as db:
            collection = db[collection_name(config.options['collection'])]
            if args.action == 'serve':
                with make_server(collection, config.options['http']) as service:
                    service.serve_forever()
            else:
                document = lookup(collection, args.language, args.key)
                if document is None:
                    raise BuildError('not_found', f'Unknown localization: {args.language}/{args.key}')
                print(json.dumps(document, ensure_ascii=False, indent=2))
    except (OSError, BuildError, KeyError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except PyMongoError as exc:
        print(f'MongoDB {type(exc).__name__}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

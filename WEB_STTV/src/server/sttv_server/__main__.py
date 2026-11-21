"""Serve the game localization API using the server's own configuration."""

import argparse
import logging
from functools import partial
from pathlib import Path

from .config import load_config
from .database import connect, selected_strings
from .http import make_server
from .technology_tooltip import technology_tooltip
from .tree.service import ReferenceTrees


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    logging.basicConfig(level=logging.INFO)
    mongo = config['mongodb']
    http = config['http']
    with connect(mongo) as client:
        collection = client[mongo['database']][mongo['collection']]
        reader = partial(selected_strings, collection)
        trees = ReferenceTrees(collection.database, config['tree_rules'], config['key_rules'], reader,
                               config.get('tree_collection_prefix', 'tree_'))
        tooltip = partial(technology_tooltip, collection.database, config['key_rules'], reader)
        with make_server((http['host'], http['port']), reader, trees, tooltip) as server:
            server.serve_forever()


if __name__ == '__main__':
    main()

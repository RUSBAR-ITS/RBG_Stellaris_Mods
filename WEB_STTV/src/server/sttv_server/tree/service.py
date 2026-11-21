"""Publish complete reference trees and coordinate opens and cleanup in the HTTP server."""

import hashlib
import json
import logging
import re
from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from time import perf_counter

from .builder import PreparedTree
from . import cards, dlcs
from .errors import BuildError, Busy, InvalidRequest


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


class ReferenceTrees:
    def __init__(self, db, options, key_rules, read_strings, prefix='tree_'):
        self.db, self.options, self.key_rules, self.read_strings = db, options, key_rules, read_strings
        if prefix != 'tree_' and not re.fullmatch(r'tree_test_[a-z0-9]+_', prefix):
            raise ValueError('Invalid tree collection prefix')
        self.prefix = prefix
        self.registry = db[prefix + 'configs']
        folder = Path(__file__).parent
        code = [hashlib.sha256(p.read_bytes()).hexdigest() for p in
                [*sorted(folder.glob('*.py')), folder.parent / 'localization.py', folder.parent / 'database.py']]
        self.rules_revision = digest([options, key_rules, code])
        self.build_lock, self.gate = Lock(), Lock()
        self.opens, self.clearing = 0, False
        self.prepared = self.prepared_revision = None
        self.cards_revision = self.cards = None

    def dlcs(self):
        return dlcs.catalog(self.db, self.key_rules, self.read_strings)

    @contextmanager
    def operation(self, clear=False):
        with self.gate:
            if self.clearing or clear and self.opens:
                raise Busy('tree_busy', 'A tree operation is in progress')
            if clear:
                self.clearing = True
            else:
                self.opens += 1
        try:
            yield
        finally:
            with self.gate:
                if clear:
                    self.clearing = False
                else:
                    self.opens -= 1

    def revision(self):
        if self.db['sttv__publication'].find_one({'_id': 'writer'}, {'_id': 1}):
            raise Busy('source_busy', 'The loader is publishing')
        names = self.options['catalogs']
        versions = sorted((r['name'], str(r['info']['uuid'])) for r in self.db.list_collections(
            filter={'name': {'$in': names}}))
        missing = set(names) - {name for name, _ in versions}
        if missing:
            raise BuildError('missing_sources', f'Missing collections: {sorted(missing)}')
        return digest(versions)

    def open(self, body):
        if not isinstance(body, dict) or set(body) - {'enabled_dlc'}:
            raise InvalidRequest('invalid_request', 'Expected reference tree settings')
        with self.operation(), self.build_lock:
            revision = self.revision()
            known = set(self.db.dlcs.distinct('_id'))
            requested = body.get('enabled_dlc', sorted(known))
            if not isinstance(requested, list) or not all(isinstance(i, str) and i in known for i in requested):
                raise InvalidRequest('invalid_dlc', 'Expected an array of known DLC IDs')
            params = {'mode': 'reference', 'enabled_dlc': sorted(set(requested))}
            identifier = digest(params)
            target = self.db[self.prefix + identifier]
            meta = {'_id': identifier, **params, 'source_revision': revision, 'rules_revision': self.rules_revision}
            if self.registry.find_one({**meta, 'state': 'ready'}) and target.name in self.db.list_collection_names(filter={'name': target.name}):
                rows = list(target.find({'availability': True}).sort('_id', 1))
            else:
                self.registry.replace_one({'_id': identifier}, {**meta, 'state': 'building'}, upsert=True)
                try:
                    start = perf_counter()
                    if self.prepared_revision != revision:
                        self.prepared = PreparedTree(self.db, self.options, self.key_rules, self.read_strings)
                        self.prepared_revision = revision
                    prepared = perf_counter() - start
                    logging.info('tree_build id=%s rules=%s enabled=%s', identifier, self.rules_revision, params['enabled_dlc'])
                    nodes, timing = self.prepared.build(params['enabled_dlc'], meta)
                    if self.revision() != revision:
                        raise Busy('source_changed', 'Input collections changed during calculation')
                    target.delete_many({})
                    target.insert_many(nodes)
                    if self.revision() != revision:
                        raise Busy('source_changed', 'Input collections changed during publication')
                    self.registry.update_one({'_id': identifier}, {'$set': {'state': 'ready',
                        'seconds': {**timing, 'preparation': prepared, 'total': perf_counter() - start}}})
                    rows = sorted((n for n in nodes if n['availability']), key=lambda n: n['_id'])
                except Exception as exc:
                    self.registry.update_one({'_id': identifier}, {'$set': {'state': 'failed', 'cause': str(exc)}})
                    raise
            if self.cards_revision != revision:
                self.cards = cards.catalog(self.db, self.key_rules)
                self.cards_revision = revision
            if self.revision() != revision:
                raise Busy('source_changed', 'Input collections changed during read')
            return {'tree_id': identifier, 'enabled_dlc': params['enabled_dlc'], 'items': rows,
                    'cards': {n['_id']: self.cards[n['_id']] for n in rows}}

    def clear(self):
        with self.operation(clear=True):
            removed = 0
            for record in self.registry.find({'mode': 'reference'}, {'_id': 1}):
                identifier = record['_id']
                if not isinstance(identifier, str) or not re.fullmatch('[a-f0-9]{64}', identifier):
                    raise BuildError('invalid_tree_id', 'Invalid reference tree registry entry')
                name = self.prefix + identifier
                if name in self.db.list_collection_names(filter={'name': name}):
                    self.db.drop_collection(name)
                    removed += 1
                self.registry.delete_one({'_id': identifier, 'mode': 'reference'})
            return {'removed_collections': removed}

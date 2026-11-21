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
from ..progress_sources import COLLECTIONS, ProgressSources


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
        self.progress_revision = self.progress = None
        self.progress_lock = Lock()
        self.tooltips = db[('' if prefix == 'tree_' else prefix) + 'technology_tooltips']
        self.tooltip_rules = digest([key_rules, [(p.name, hashlib.sha256(p.read_bytes()).hexdigest())
            for p in sorted([*folder.parent.glob('*.py'), *folder.glob('*.py'),
                             folder.parent.parent / 'config' / 'condition_rules.json',
                             folder.parent.parent / 'config' / 'acquisition_rules.json']) if p.is_file()]])

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

    def revision(self, names=None):
        if self.db['sttv__publication'].find_one({'_id': 'writer'}, {'_id': 1}):
            raise Busy('source_busy', 'The loader is publishing')
        names = self.options['catalogs'] if names is None else names
        versions = sorted((r['name'], str(r['info']['uuid'])) for r in self.db.list_collections(
            filter={'name': {'$in': names}}))
        missing = set(names) - {name for name, _ in versions}
        if missing:
            raise BuildError('missing_sources', f'Missing collections: {sorted(missing)}')
        return digest(versions)

    def technology_tooltip(self, identifier, language, enabled=None):
        from ..technology_tooltip import prepare_tooltip
        from ..tooltip_document import render
        from .inputs import records
        from .ast import scalar

        names = sorted({*COLLECTIONS, 'technologies', 'dlcs', 'localization', 'policies', 'bypass',
                        'components', 'global_ship_designs', 'components_provenance', 'global_ship_designs_provenance',
                        'technologies_provenance', 'script_history', *(name + '_provenance' for name in COLLECTIONS)})
        with self.operation():
            selection = None
            if enabled is not None:
                available = {r['id']: scalar(r['body'], 'name') for r in records(self.db, 'dlcs', ['name'])}
                if not isinstance(enabled, list) or any(not isinstance(k, str) or k not in available for k in enabled):
                    raise InvalidRequest('invalid_dlc', 'Expected known DLC IDs')
                selection = {available[k] for k in enabled}
            with self.progress_lock:
                revision = self.revision(names)
                identity = {'_id': identifier, 'source_revision': revision, 'rules_revision': self.tooltip_rules}
                document = self.tooltips.find_one(identity)
                if document is None:
                    if self.progress_revision != revision:
                        start = perf_counter()
                        self.progress = ProgressSources.build(self.db)
                        self.progress_revision = revision
                        logging.info('technology_acquisition_build revision=%s seconds=%.3f',
                                     revision, perf_counter() - start)
                    document = prepare_tooltip(self.db, self.key_rules, identifier, self.progress)
                    if self.revision(names) != revision:
                        raise Busy('source_changed', 'Technology inputs changed during preparation')
                    if document is None:
                        return None
                    self.tooltips.replace_one({'_id': identifier}, {**identity, **document}, upsert=True)
            result = render(document, self.key_rules, self.read_strings, language, selection)
            if self.revision(names) != revision:
                raise Busy('source_changed', 'Technology inputs changed during lookup')
            return result

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

    def clear(self, scope='trees'):
        with self.operation(clear=True):
            removed = 0
            if scope in ('progress', 'all'):
                self.progress = self.progress_revision = None
            if scope in ('tooltips', 'progress', 'all'):
                self.tooltips.delete_many({})
            if scope in ('tooltips', 'progress'):
                return {'removed_collections': 0}
            for record in self.registry.find({'mode': 'reference'}, {'_id': 1}):
                identifier = record['_id']
                if not isinstance(identifier, str) or not re.fullmatch('[a-f0-9]{64}', identifier):
                    raise BuildError('invalid_tree_id', 'Invalid reference tree registry entry')
                name = self.prefix + identifier
                if name in self.db.list_collection_names(filter={'name': name}):
                    self.db.drop_collection(name)
                    removed += 1
                self.registry.delete_one({'_id': identifier, 'mode': 'reference'})
            self.prepared = self.prepared_revision = self.cards = self.cards_revision = None
            return {'removed_collections': removed}

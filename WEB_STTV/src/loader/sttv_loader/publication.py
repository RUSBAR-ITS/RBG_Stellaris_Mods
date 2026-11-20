"""Stage a complete load and recover interrupted collection replacements."""

import os
import socket
from contextlib import contextmanager
from uuid import uuid4

from document_package.errors import BuildError
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError


CONTROL = 'sttv__publication'


@contextmanager
def local_lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+b') as stream:
        stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise BuildError('loader_busy', 'Another loader is using this working directory') from exc
        yield


def recover(db, state):
    """Undo an incomplete promotion or finish cleanup of a committed one."""
    existing = set(db.list_collection_names())
    phase = state.get('phase')
    for item in reversed(state.get('plan', [])):
        name, stage, backup = item['name'], item['stage'], item['backup']
        if phase == 'promoting':
            if backup in existing:
                db[backup].rename(name, dropTarget=True)
            elif not item['existed'] and stage not in existing and name in existing:
                db.drop_collection(name)
        elif phase == 'committed' and backup in existing:
            db.drop_collection(backup)
        if stage in existing:
            db.drop_collection(stage)
    db[CONTROL].update_one({'_id': 'writer'}, {'$unset': {'phase': '', 'plan': ''}})


@contextmanager
def writer(db, scratch):
    lock_path = (scratch / 'publication.lock').resolve()
    owner = f'{socket.gethostname()}/{os.path.normcase(str(lock_path))}'
    with local_lock(lock_path):
        try:
            state = db[CONTROL].find_one_and_update(
                {'_id': 'writer', 'owner': owner}, {'$setOnInsert': {'owner': owner}},
                upsert=True, return_document=ReturnDocument.AFTER)
        except DuplicateKeyError as exc:
            raise BuildError('loader_busy', 'Another loader workspace owns this database') from exc
        try:
            if state.get('plan'):
                recover(db, state)
            yield
        finally:
            # Retain a pending plan if the database was unreachable during rollback.
            db[CONTROL].delete_one({'_id': 'writer', 'owner': owner, 'plan': {'$exists': False}})


def create(db, names):
    existing = set(db.list_collection_names())
    for name in names:
        if name not in existing:
            db.create_collection(name)


def promote(db, plan):
    for item in plan:
        if item['existed']:
            db[item['name']].rename(item['backup'])
        db[item['stage']].rename(item['name'])


@contextmanager
def staging(db, names):
    existing = set(db.list_collection_names())
    token = uuid4().hex
    plan = [{'name': name, 'stage': f'sttv__new_{token}_{i}', 'backup': f'sttv__old_{token}_{i}',
             'existed': name in existing} for i, name in enumerate(names)]
    journal = db[CONTROL]
    journal.update_one({'_id': 'writer'}, {'$set': {'phase': 'staging', 'plan': plan}})
    try:
        for item in plan:
            db.create_collection(item['stage'])
        yield {item['name']: db[item['stage']] for item in plan}
        journal.update_one({'_id': 'writer'}, {'$set': {'phase': 'promoting'}})
        promote(db, plan)
        journal.update_one({'_id': 'writer'}, {'$set': {'phase': 'committed'}})
    finally:
        state = journal.find_one({'_id': 'writer'})
        if state is None:
            raise BuildError('publication_journal', 'Publication journal disappeared')
        recover(db, state)

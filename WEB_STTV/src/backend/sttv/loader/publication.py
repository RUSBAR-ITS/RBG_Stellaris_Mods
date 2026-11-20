"""Verify by typed identifier and atomically replace one collection."""

from uuid import uuid4

from bson import BSON
from document_package.errors import BuildError


def identity(row):
    return BSON.encode({'_id': row['_id']})


def canonical(value):
    if isinstance(value, dict):
        return {key: canonical(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [canonical(item) for item in value]
    return value


def verify(collection, package):
    seen = set()
    for batch in package.batches():
        expected = {}
        for row in batch:
            key = identity(row)
            if key in seen:
                raise BuildError('duplicate_id', f'Duplicate package _id: {row["_id"]!r}')
            seen.add(key)
            expected[key] = row
        query = {'_id': {'$in': [row['_id'] for row in batch]}}
        with collection.find(query) as cursor:
            for actual in cursor:
                row = expected.pop(identity(actual), None)
                if row is None or BSON.encode(canonical(actual)) != BSON.encode(canonical(row)):
                    raise BuildError('document_mismatch', f'Document differs at _id {actual["_id"]!r}')
        if expected:
            missing = next(iter(expected.values()))
            raise BuildError('document_mismatch', f'Missing _id: {missing["_id"]!r}')
    if not seen and collection.name not in collection.database.list_collection_names(filter={'name': collection.name}):
        raise BuildError('missing_collection', f'Unpublished collection: {collection.full_name}')
    if collection.count_documents({}) != len(seen):
        raise BuildError('document_mismatch', 'Published collection has extra documents')
    return len(seen)


def publish(target, package):
    staging = target.database.create_collection(f'{target.name}__loading_{uuid4().hex}')
    try:
        for batch in package.batches():
            staging.insert_many(batch)
        count = verify(staging, package)
        staging.rename(target.name, dropTarget=True)
    except BaseException:
        staging.drop()
        raise
    return count

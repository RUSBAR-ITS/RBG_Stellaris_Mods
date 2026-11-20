"""Load, reconstruct and verify typed BSON records in bounded batches."""

from collections import defaultdict

from bson import BSON
from document_package.errors import BuildError

from .provenance import restore_tree, split_tree


MAX_DOCUMENT = 16 * 1024 * 1024
BATCH_BYTES = 4 * 1024 * 1024


def typed_id(row):
    return BSON.encode({'_id': row['_id']})


def prepare(record):
    document = record.document
    main = {'_id': document['_id'], **document}
    documents = [(record.collection, main)]
    if record.provenance:
        tree, locations = split_tree(document['tree'], document['_id'])
        main['tree'] = tree
        documents.append((record.provenance, locations))
    size = 0
    for name, row in documents:
        length = len(BSON.encode(row))
        if length > MAX_DOCUMENT:
            raise BuildError('document_too_large', f'{name}/{row["_id"]!r}: {length} BSON bytes')
        size += length
    return documents, size


def check_batch(targets, batch, writing):
    grouped = defaultdict(list)
    for _, documents in batch:
        for name, row in documents:
            grouped[name].append(row)
    actual = {}
    for name, rows in grouped.items():
        collection = targets[name]
        if writing:
            collection.insert_many(rows)
        keys = [row['_id'] for row in rows]
        with collection.find({'_id': {'$in': keys}}) as cursor:
            found = {typed_id(row): row for row in cursor}
        for row in rows:
            value = found.get(typed_id(row))
            if value is None or BSON.encode(value) != BSON.encode(row):
                raise BuildError('document_mismatch', f'{name}/{row["_id"]!r}: missing or different document')
        actual[name] = found
    for record, documents in batch:
        if record.provenance:
            key = typed_id(record.document)
            tree = restore_tree(actual[record.collection][key], actual[record.provenance][key])
            if BSON.encode({'tree': tree}) != BSON.encode({'tree': record.document['tree']}):
                raise BuildError('tree_mismatch', f'{record.collection}/{record.document["_id"]!r}')


def transfer(inputs, targets, *, writing):
    seen = {name: set() for name in targets}
    batch = []
    size = 0
    for record in inputs.records():
        documents, length = prepare(record)
        for name, row in documents:
            key = typed_id(row)
            if key in seen[name]:
                raise BuildError('duplicate_id', f'Duplicate object in {name}: {row["_id"]!r}')
            seen[name].add(key)
        if batch and (size + length > BATCH_BYTES or len(batch) >= 500):
            check_batch(targets, batch, writing)
            batch = []
            size = 0
        batch.append((record, documents))
        size += length
    if batch:
        check_batch(targets, batch, writing)
    counts = {}
    for name, collection in targets.items():
        counts[name] = len(seen[name])
        if collection.count_documents({}) != counts[name]:
            raise BuildError('document_mismatch', f'Unexpected document count in {name}')
    return counts

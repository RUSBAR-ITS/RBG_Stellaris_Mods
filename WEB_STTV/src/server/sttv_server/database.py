"""Read the selected localization definitions using their compound identifiers."""

import os

from pymongo import MongoClient


def connect(options):
    return MongoClient(
        options['host'], options['port'], directConnection=True,
        username=options['username'], password=os.environ[options['password_env']],
        authSource=options['auth_source'], authMechanism='SCRAM-SHA-256',
        tls=True, tlsCAFile=options['ca_file'], serverSelectionTimeoutMS=5000,
        appname='sttv-server',
    )


def selected_strings(collection, language, keys):
    for start in range(0, len(keys), 1000):
        ids = [{'language': language, 'key': key} for key in keys[start:start + 1000]]
        pipeline = [
            {'$match': {'_id': {'$in': ids}}},
            {'$project': {'text': {'$arrayElemAt': ['$definitions.raw', '$selected']}}},
        ]
        with collection.aggregate(pipeline) as rows:
            for row in rows:
                yield row['_id']['key'], row['text']

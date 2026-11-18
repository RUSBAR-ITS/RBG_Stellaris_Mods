"""Parallel execution configuration and operation measurements."""

from .helpers import HASH, NULL, RELATIVE, TEXT, array, mapping, obj, union


def configuration():
    return obj({'format_version': {'const': 1}, 'workers': {'type': 'integer', 'minimum': 1},
                'staging_directory': RELATIVE})


def performance():
    count, seconds = {'type': 'integer', 'minimum': 0}, {'type': 'number', 'minimum': 0}
    job = obj({'index': count, 'source': TEXT, 'status': {'enum': ['success', 'failed', 'cancelled', 'not_started']},
        'pid': union(count, NULL), 'seconds': seconds, 'bytes': count,
        'content_hash': union(HASH, NULL), 'shard_hash': union(HASH, NULL)})
    worker = obj({'pid': count, 'seconds': seconds, 'rule_seconds': seconds, 'bytes': count,
                  'counts': mapping(count), 'timings': mapping(seconds)})
    return obj({'configured_workers': count, 'used_workers': count,
                'identity_algorithm': {'const': 'sttv.document_hashes.v1'},
                'jobs': array(job), 'workers': array(worker),
                'memory': obj({'method': {'enum': ['windows_working_set_sample', 'unavailable']},
                    'interval_seconds': seconds, 'samples': count, 'coordinator_peak_bytes': count,
                    'tree_peak_bytes': count, 'temporary_peak_bytes': count, 'errors': count})})

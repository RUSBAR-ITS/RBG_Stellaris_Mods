"""Project independent documents in bounded processes and return no syntax trees."""

from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from time import perf_counter

from sttv.storage.reading import read
from sttv.common.errors import BuildError
from .inputs import record_for


def project_job(job):
    kind, path, descriptor, objects, wanted = job
    identifier = descriptor['document_id']
    def extract(pointer, node):
        record = record_for(kind, identifier, pointer, node)
        return record if record and (wanted is None or record['id'] in wanted) else None
    try:
        records, verification = read(path, kind, descriptor, objects, extract)
        return {'kind': kind, 'identifier': identifier, 'records': records, 'verification': verification}
    except Exception as exc:
        return {'error': {'code': getattr(exc, 'code', 'projection_failed'),
                         'message': str(exc), 'details': getattr(exc, 'context', {})}}


class Projections:
    def __init__(self, reader, workers):
        self.reader, self.workers = reader, workers

    def __enter__(self):
        self.pool = ProcessPoolExecutor(max_workers=self.workers, mp_context=get_context('spawn'))
        return self

    def __exit__(self, *_):
        self.pool.shutdown(wait=True, cancel_futures=True)

    def load(self, kinds, wanted=None):
        reader, jobs = self.reader, []
        result = {kind: [] for kind in kinds}
        for kind in kinds:
            selected = (None if wanted is None else {ref['document_id'] for identifier in wanted
                        for ref in reader.resolve_object(kind, identifier)})
            for identifier in reader.document_ids(kind):
                if selected is not None and identifier not in selected:
                    continue
                key = kind, identifier
                jobs.append((kind, reader.paths[key], reader.descriptors[key], reader.objects[key], wanted))
        start = perf_counter()
        for offset in range(0, len(jobs), self.workers):
            for row in self.pool.map(project_job, jobs[offset:offset + self.workers]):
                if 'error' in row:
                    failure = row['error']
                    error = BuildError(failure['code'], failure['message'])
                    error.context = {**failure['details'], 'snapshot_revision': reader.manifest['snapshot_revision']}
                    raise error
                kind, identifier, verification = row['kind'], row['identifier'], row['verification']
                result[kind].extend(row['records'])
                reader.verified[(kind, identifier)] = verification['signature']
                reader.bytes += verification['bytes']
        reader.seconds += perf_counter() - start
        return result

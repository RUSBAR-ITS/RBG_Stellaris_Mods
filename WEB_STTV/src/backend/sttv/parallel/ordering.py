"""Assign existing cumulative invocation IDs without moving document trees."""

from queue import Empty

from sttv.common.errors import BuildError
from sttv.common.timing import measure


def invocation_counts(expansion, seed):
    counts = {'inline': expansion.counts['encountered']}
    for kind, values in expansion.library.counts.items():
        counts[kind] = values['encountered'] - seed['counts']['scripted_calls'][kind]['encountered']
    return counts


def offsets(job, expansion, seed, transport, timings):
    requests, response, rank = transport
    requests.put((job['kind'], job['index'], rank, invocation_counts(expansion, seed)))
    with measure(timings, 'id_order_wait'):
        message = response.get()
    if message is None:
        raise BuildError('parallel_cancelled', 'Build cancelled before document serialization')
    kind, index, values = message
    if (kind, index) != (job['kind'], job['index']):
        raise BuildError('parallel_order', 'Unexpected invocation-order response')
    return values


class Ordering:
    def __init__(self, kind, count, requests, responses):
        self.kind, self.count = kind, count
        self.requests, self.responses = requests, responses
        self.pending, self.seen, self.next, self.total = {}, set(), 0, {}
        self.cancelled = False

    def receive(self):
        while True:
            try:
                kind, index, rank, counts = self.requests.get_nowait()
            except Empty:
                break
            if self.cancelled:
                self.responses[rank].put(None)
                continue
            if kind != self.kind or not 0 <= index < self.count or index in self.seen:
                self.responses[rank].put(None)
                raise BuildError('parallel_order', 'Repeated or foreign invocation counts')
            self.seen.add(index)
            self.pending[index] = rank, counts
        while self.next in self.pending and not self.cancelled:
            rank, counts = self.pending.pop(self.next)
            self.responses[rank].put((self.kind, self.next, dict(self.total)))
            for kind, amount in counts.items():
                self.total[kind] = self.total.get(kind, 0) + amount
            self.next += 1

    def abort(self):
        if not self.cancelled:
            self.cancelled = True
            for rank, _ in self.pending.values():
                self.responses[rank].put(None)
            self.pending.clear()

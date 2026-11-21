from collections import defaultdict
from .errors import BuildError


class Catalog:
    def __init__(self, records):
        self.records = records
        self.providers = {}
        self.by_id = {}
        for kind, rows in records.items():
            index = defaultdict(list)
            for row in rows:
                index[row['id']].append(row)
            self.by_id[kind] = index

    def resolve(self, kind, key, *, fragments=False, required=False):
        rows = self.by_id.get(kind, {}).get(key, [])
        if not rows and required:
            raise BuildError('missing_object', f'Unresolved object: {kind}/{key}')
        if len(rows) > 1 and not fragments:
            raise BuildError('ambiguous_object', f'Ambiguous object: {kind}/{key}')
        return rows if fragments else rows[0] if rows else None

    def rows(self, kind):
        return self.records[kind]

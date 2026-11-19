"""Document-local indexes filled by prepared structural handlers."""

from sttv.database.history import check_history
from sttv.database.enrichment import validate_enrichments
from sttv.common.errors import BuildError
import re


class DocumentContext:
    def __init__(self, document, prefix):
        self.prefix = prefix
        self.document = document
        self.nodes, self.origins, self.enriched = {}, {}, {}
        self.containers = {'/items': document.get('items') if isinstance(document, dict) else None}
        self.count = 0

    def node(self, path, value):
        self.count += 1
        local = path[len(self.prefix):]
        if value['kind'] == 'script_value':
            self.nodes[local] = value
        if 'items' in value:
            self.containers[local + '/items'] = value['items']
        if 'localization' in value.get('enrichments', {}):
            self.enriched[path] = value
        if ('technology_tree' in value.get('enrichments', {})
                and (self.document.get('database') != 'technologies'
                     or not re.fullmatch(r'/items/\d+', local))):
            raise BuildError('invalid_tree_target', 'Technology tree enrichment requires a root object', field_path=path)

    def origin(self, path, value):
        if value['expansion_id'] is not None:
            self.origins.setdefault(value['expansion_id'], path)

    def finish(self, document):
        check_history(document, self.nodes, self.containers, self.origins, self.prefix)
        validate_enrichments(self.enriched, self.document)

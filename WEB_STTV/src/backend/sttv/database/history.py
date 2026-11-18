"""Check expansion references using indexes from structural validation."""

from sttv.common.errors import BuildError


def invalid(message, path):
    raise BuildError('invalid_inline_history', message, field_path=path)


def check_history(document, nodes, containers, origins, prefix):
    records = document['metadata']['expansions']
    calls = {record['id']: record for record in records}
    if len(calls) != len(records):
        invalid('Duplicate invocation identifier', prefix + '/metadata/expansions')
    ancestors = {}
    for identifier in calls:
        trail, current = [], identifier
        while current is not None and current not in ancestors:
            if current in trail or current not in calls:
                invalid('Cyclic or missing invocation parent', prefix + '/metadata/expansions')
            trail.append(current)
            current = calls[current]['parent_id']
        inherited = ancestors.get(current, frozenset())
        for item in reversed(trail):
            inherited = inherited | {item}
            ancestors[item] = inherited
    for identifier, path in origins.items():
        if identifier not in calls:
            invalid(f'Unknown invocation in provenance: {identifier}', path)
    for path, node in nodes.items():
        record = calls.get(node['origin']['expansion_id'], {})
        if record.get('kind') != 'script_value' or record.get('insertion') != {'node': path}:
            invalid('Calculation node is missing its own history entry', prefix + path)
    for index, record in enumerate(records):
        insertion = record['insertion']
        path = f'{prefix}/metadata/expansions/{index}/insertion'
        if record['kind'] == 'script_value':
            node = nodes.get(insertion.get('node'))
            if node is None or node['origin']['expansion_id'] != record['id']:
                invalid('Value insertion does not address its calculation node', path)
            continue
        sequence = containers.get(insertion['container'])
        start, count = insertion['index'], insertion['count']
        if sequence is None or start + count > len(sequence):
            invalid('Insertion does not address a valid syntax sequence range', path)
        for offset in range(int(start), int(start + count)):
            call = sequence[offset]['origin']['expansion_id']
            if record['id'] not in ancestors.get(call, ()):
                invalid('Inserted node provenance does not belong to the invocation', path)


def validate_history(document):
    """Use the shared document audit for standalone parser diagnostics."""
    from .validation import DatabaseValidator
    DatabaseValidator().document(document, 0)

"""Validate new relationship records and revisions, without revisiting game semantics."""

from jsonschema import Draft202012Validator

from sttv.common.errors import BuildError
from sttv.schema_generation.technology_tree import RESULT, metadata as metadata_schema
from .revisions import digest, calculation_revision, result_revision, rules_revision


def check_results(results, technologies=None):
    validator = Draft202012Validator(RESULT)
    if technologies is not None and results.keys() != technologies.keys():
        raise BuildError('incomplete_tree', 'Tree records do not match selected technologies')
    for key, row in results.items():
        error = next(validator.iter_errors(row), None)
        if error:
            raise BuildError('invalid_tree', f'{key}: {error.message}')
        parent = row['parent_tech']
        visible = row.get('visibility', {}).get('visible', True)
        if not visible and (parent is not None or row['children'] or row['status'] != 'root'):
            raise BuildError('invalid_tree', f'{key}: hidden technology has tree links')
        if parent is not None and not results.get(parent, {}).get('visibility', {}).get('visible', True):
            raise BuildError('invalid_tree', f'{key}: hidden parent')
        if (row['status'] == 'resolved') != (parent is not None):
            raise BuildError('invalid_tree', f'{key}: status disagrees with parent')
        if row['children'] != sorted(row['children']):
            raise BuildError('invalid_tree', f'{key}: noncanonical child order')
        if parent is not None and (parent not in results or key not in results[parent]['children']):
            raise BuildError('nonreciprocal_tree', f'{key}: missing reverse parent link')
        if any(child not in results or results[child]['parent_tech'] != key for child in row['children']):
            raise BuildError('nonreciprocal_tree', f'{key}: invalid child link')
        if technologies is not None:
            candidates = technologies[key]['parents']
            if 'visibility' in row:
                candidates = [p for p in candidates if results[p]['visibility']['visible']] if visible else []
            if parent is not None and parent not in candidates:
                raise BuildError('invalid_parent', f'{key}: parent is not an original prerequisite')
            if (row['status'] == 'root') != (not candidates) or row['status'] == 'ambiguous' and len(candidates) < 2:
                raise BuildError('invalid_tree', f'{key}: status disagrees with prerequisites')
    done = set()
    for key in results:
        path, current = set(), key
        while current is not None and current not in done:
            if current in path:
                raise BuildError('tree_cycle', f'Selected parent cycle at {current}')
            path.add(current)
            current = results[current]['parent_tech']
        done.update(path)


def check_metadata(meta, results):
    error = next(Draft202012Validator(metadata_schema()).iter_errors(
        {'format_version': 1, 'combinations': {'check': meta}}), None)
    if error:
        raise BuildError('invalid_tree_metadata', error.message)
    inputs = meta['inputs']
    if len({row['kind'] for row in inputs}) != len(inputs) or inputs != sorted(inputs, key=lambda r: r['kind']):
        raise BuildError('invalid_tree_metadata', 'Input inventory must be unique and ordered')
    expected = {'input_revision': digest({'source_set_id': meta['source_set_id'], 'inputs': inputs}),
                'rules_revision': rules_revision(meta), 'parameters_revision': digest(meta['parameters']),
                'calculation_revision': calculation_revision(meta), 'result_revision': result_revision(meta, results)}
    if any(meta[key] != value for key, value in expected.items()):
        raise BuildError('tree_revision', 'Relationship revision mismatch')
    if meta['parameters']['variants'].keys() != results.keys():
        raise BuildError('invalid_tree_metadata', 'Variant selection does not cover the result')

"""Check localization integrity without loading configurations or game files."""

from sttv.common.errors import BuildError


def invalid(message, path):
    raise BuildError("invalid_localization", message, field_path=path)


def validate_fallback(node, path, name, field):
    reference = field['fallback']['source_ref']
    prefix = path + '/value/items/'
    if (name != 'description' or field['inherited_from'] is not None
            or not reference.startswith(prefix) or not reference[len(prefix):].isdigit()):
        invalid('Invalid shared component description reference', path)
    index = int(reference[len(prefix):])
    items = node['value']['items']
    if index >= len(items):
        invalid('Shared description reference is outside this component', path)
    shared = items[index]
    identifiers = [child['value']['text'] for child in items if child['kind'] == 'assignment'
                   and child['key']['text'] == 'key' and child['value']['kind'] == 'scalar']
    if (len(identifiers) != 1 or shared['kind'] != 'assignment'
            or shared['key']['text'] != 'component_set' or shared['value']['kind'] != 'scalar'
            or not field['requested_key'].startswith(identifiers[0])):
        invalid('Shared description does not reference a component set field', path)
    suffix = field['requested_key'][len(identifiers[0]):]
    if not suffix or field['key'] != shared['value']['text'] + suffix:
        invalid('Shared description key does not match the referenced component set', path)


def validate_enrichments(enriched):
    for path, node in enriched.items():
        if node['kind'] != 'assignment' or node["operator"] != "=" or node["value"]["kind"] not in ('block', 'scalar'):
            invalid("Localization requires a block or scalar assignment", path)
        localized = node['enrichments']['localization']
        if set(localized['ru']) != set(localized['en']):
            invalid('Localized roles differ between languages', path)
        for language, fields in node["enrichments"]["localization"].items():
            for name, field in fields.items():
                if field['requested_key'] != localized['en' if language == 'ru' else 'ru'][name]['requested_key']:
                    invalid('Requested localization keys differ between languages', path)
                if field["key"] is None:
                    if (any(field[key] is not None for key in ("raw", "text", "source", "inherited_from"))
                            or field["unresolved_references"] or 'fallback' in field):
                        invalid("Missing text must have no selection or inheritance", path)
                    continue
                if any(field[key] is None for key in ("raw", "text", "source")):
                    invalid("Found text must include raw, resolved text and source", path)
                if 'fallback' in field:
                    validate_fallback(node, path, name, field)
                    continue
                parent = field["inherited_from"]
                if parent is None:
                    if field["key"] != field["requested_key"]:
                        invalid("Direct text must match its requested key", path)
                    continue
                if (name != "description" or parent not in enriched
                        or path.rsplit("/value/items/", 1)[0] != parent):
                    invalid("Inheritance must reference the enclosing base technology", path)
                original = enriched[parent]["enrichments"]["localization"][language][name]
                if original["inherited_from"] is not None or original["key"] is None:
                    invalid("The inherited base description must be found and direct", path)
                if any(field[key] != original[key] for key in
                       ("key", "raw", "text", "source", "unresolved_references")):
                    invalid("Inherited text and source must match the base description", path)

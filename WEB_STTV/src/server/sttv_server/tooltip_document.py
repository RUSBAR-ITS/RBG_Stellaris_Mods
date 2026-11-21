"""Store language-independent tooltip content with a table of reusable phrase references."""

from dataclasses import fields
import json

from .tooltip_labels import Label, Labels


def pack(labels, content):
    references, positions = [], {}

    def encode(value):
        if isinstance(value, Label):
            record = {f.name: encode(getattr(value, f.name)) for f in fields(Label)
                      if getattr(value, f.name) is not None}
            key = json.dumps(record, sort_keys=True, ensure_ascii=False)
            if key not in positions:
                positions[key] = len(references)
                references.append(record)
            return {'phrase_ref': positions[key]}
        if isinstance(value, (list, tuple)):
            return [encode(child) for child in value]
        if isinstance(value, dict):
            return {key: encode(child) for key, child in value.items()}
        return value

    fragments, fragment_ids = [], {}

    def intern(value):
        if isinstance(value, list):
            return [intern(item) for item in value]
        if not isinstance(value, dict):
            return value
        item = {key: intern(child) for key, child in value.items()}
        if 'kind' not in item or not ('text' in item or 'children' in item):
            return item
        signature = json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        if signature not in fragment_ids:
            fragment_ids[signature] = len(fragments)
            fragments.append(item)
        return {'fragment_ref': fragment_ids[signature]}

    unique_issues = {json.dumps(issue, sort_keys=True): issue for issue in labels.diagnostics}
    return {'content': intern(encode(content)), 'fragments': fragments, 'phrases': references,
            'keys': sorted(labels.keys), 'diagnostics': list(unique_issues.values())}


def render(document, rules, reader, language, enabled):
    labels = Labels(language, rules, None)
    labels.keys.update(document['keys'])
    labels.diagnostics.extend(document['diagnostics'])
    references = []
    fragments = []

    def decode(value):
        if isinstance(value, list):
            return [decode(child) for child in value]
        if isinstance(value, dict):
            if set(value) == {'phrase_ref'}:
                return references[value['phrase_ref']]
            if set(value) == {'fragment_ref'}:
                return fragments[value['fragment_ref']]
            return {key: decode(child) for key, child in value.items()}
        return value

    for record in document['phrases']:
        references.append(Label(**{'fallback': None, **decode(record)}))
    for fragment in document['fragments']:
        fragments.append(decode(fragment))
    return labels.resolve({**decode(document['content']), 'language': language}, reader, enabled)

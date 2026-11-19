"""Use the established localization tiers and reference resolver for categories."""

from sttv.enrichment.localization.index import LocalizationIndex
from sttv.enrichment.localization.references import Resolver


def prepare_categories(identifiers, settings, snapshot, report):
    index = LocalizationIndex(settings.localization, snapshot, report)
    resolver = Resolver(index, settings.localization.options['references'])
    result = {}
    for language in settings.localization.options['languages']:
        report['counts'][f'categories_{language}'] = 0
    for identifier in sorted(identifiers):
        key = settings.options['category_key'].format(id=identifier)
        result[identifier] = {}
        for language in settings.localization.options['languages']:
            resolved = resolver.resolve(language, key)
            if resolved is not None:
                report['counts'][f'categories_{language}'] += 1
            if resolved is None:
                report['diagnostics'].append({'severity': 'warning', 'code': 'missing_localization',
                                              'language': language, 'category': identifier, 'key': key})
            result[identifier][language] = {'requested_key': key, 'key': key if resolved else None,
                'raw': resolved['raw'] if resolved else None, 'text': resolved['text'] if resolved else None,
                'source': resolved['source'] if resolved else None, 'inherited_from': None,
                'unresolved_references': resolved['unresolved_references'] if resolved else []}
    return result, index

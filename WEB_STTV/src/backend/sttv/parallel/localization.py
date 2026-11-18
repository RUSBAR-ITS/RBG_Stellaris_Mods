"""Reuse source tables while isolating each document's selected-key inventory."""

from copy import copy

from sttv.libraries.inventory import digest
from sttv.enrichment.localization.index import LocalizationIndex
from sttv.enrichment.localization.report import new_report, failed
from sttv.enrichment.localization.snapshot import Snapshot
from sttv.enrichment.localization.selection import select_targets
from sttv.enrichment.localization.attachment import attach
from sttv.common.errors import BuildError
from sttv.common.timing import measure
from .text_cache import CachedResolver


class Localizations:
    def __init__(self):
        self.tables = {}
        self.texts = {}

    def apply(self, document, settings, ordinal, report, identities, timings):
        key = digest({'sources': {lang: [(tier, str(path)) for tier, path in sources]
                                 for lang, sources in settings.sources.items()},
                      'reading': settings.options['reading'], 'languages': settings.options['languages']})
        if key not in self.tables:
            with measure(timings, 'localization_load'):
                seed = new_report()
                snapshot = Snapshot(seed)
                index = LocalizationIndex(settings, snapshot, seed)
            self.tables[key] = (index, seed)
        base, seed = self.tables[key]
        index = copy(base)
        index.selected = {}
        index.report = report
        report['inputs'] = seed['inputs']
        report['duplicates'] = seed['duplicates']
        container = {'documents': [document]}
        targets = select_targets(container, settings, report['counts'],
                                 document_offset=ordinal, identities=identities)
        reference_key = key, digest(settings.options['references'])
        resolver = CachedResolver(index, settings.options['references'], self.texts.setdefault(reference_key, {}))
        attach(container, targets, settings, resolver, report, fresh=True)
        report['selected_sources'] = [index.selected[key] for key in sorted(index.selected)]
        if failed(report):
            raise BuildError('member_localization_failed', 'Localization failed; see document diagnostics')
        return index.file_sets

"""Reuse resolved texts while replaying only the current lookup's sources."""

from copy import copy

from sttv.enrichment.localization.references import Resolver


class CachedResolver:
    def __init__(self, index, options, entries):
        self.index, self.options, self.entries = index, options, entries

    def resolve(self, language, key):
        identity = language, key
        if identity not in self.entries:
            lookup = copy(self.index)
            lookup.selected = {}
            value = Resolver(lookup, self.options).resolve(language, key)
            self.entries[identity] = value, lookup.selected
        value, selected = self.entries[identity]
        self.index.selected.update(selected)
        return value

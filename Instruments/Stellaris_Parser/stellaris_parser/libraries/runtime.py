"""Expansion using an in-memory library set and fresh state per document."""

from collections import Counter
from copy import copy

from document_package.errors import BuildError
from ..script.inline import Expansion
from ..script.inlining.loader import exception_files, template_name
from ..script.parser import parse_text
from ..script.scripted.index import Index
from ..script.serialization import serialize_document
from ..script.variables.processor import Processor


class Templates:
    def __init__(self, settings, sources):
        self.sources = sources
        self.extension = settings.inline['extension']
        self.exceptions = exception_files(settings.exceptions)
        self.manifest = {}

    def identity(self, name):
        key = template_name(name, '').casefold()
        relative = self.exceptions.get(key, template_name(name, self.extension))
        if relative.casefold() not in self.sources:
            raise BuildError('missing_inline_template', f'Missing inline template: {relative}')
        return relative.casefold(), relative, None

    def read(self, name):
        key, relative, _ = self.identity(name)
        source = self.sources[key]
        self.manifest[relative] = True
        return source


class Runtime:
    def __init__(self, settings, catalogs):
        self.settings = settings
        self.shared = catalogs['static_variables']['definitions']
        self.templates = Templates(settings, catalogs['inline_script']['definitions'])
        self.index = Index(settings.calls)
        self.index.value_options = settings.values
        for kind in ('scripted_effect', 'scripted_trigger'):
            self.index.entries.update(catalogs[kind]['definitions'])
        self.index.values = catalogs['script_value']['definitions']

    def parse(self, relative, path):
        settings = self.settings
        variables = Processor(settings.rules, self.shared, Counter())
        index = copy(self.index)
        index.counts = {kind: counts.copy() for kind, counts in self.index.counts.items()}
        templates = copy(self.templates)
        templates.manifest = {}
        expansion = Expansion(templates, settings.inline, library=index, variables=variables,
                              exceptions=settings.source_corrections())
        text = path.read_text(encoding=settings.reading['encoding'])
        document = parse_text(text, settings.syntax, relative, expansion=expansion)
        return serialize_document(variables.apply(document))

"""Retain one prepared graph across explicit profile applications in a service session."""

from sttv.common.errors import BuildError
from sttv.storage.identity import digest
from .analysis import Analysis


class AnalysisCache:
    def __init__(self):
        self.key, self.analysis = None, None

    def get(self, technologies, names, rules, reader, cancelled=None):
        key = digest([str(reader.root), reader.manifest['set_id'], rules, names,
                      {k: v.get('variant', 'base') for k, v in sorted(technologies.items())}])
        if key != self.key:
            analysis = Analysis(technologies, names, rules, reader=reader, cancelled=cancelled)
            self.key, self.analysis = key, analysis
            analysis.graph.statistics['reused_graph'] = False
            return analysis
        analysis = self.analysis
        previous = analysis.library.reader
        for identity, verified in previous.verified.items():
            if identity[0] == 'technologies':
                continue
            previous.check_document(identity)
            if identity[0] != 'acquisition' and reader.paths[identity] != previous.paths[identity]:
                raise BuildError('acquisition_cache', 'Cached dependency path changed without a source revision')
            reader.paths[identity] = previous.paths[identity]
            reader.verified[identity] = verified
        for identity, value in previous.cache.items():
            if identity not in reader.cache:
                reader.cache[identity] = value
        analysis.library.reader = reader
        if analysis.compiler.acquisition and analysis.compiler.acquisition.index:
            analysis.compiler.acquisition.index.reader = reader
        analysis.graph.cancelled = cancelled
        analysis.graph.statistics['reused_graph'] = True
        return analysis

    def clear(self):
        self.key, self.analysis = None, None

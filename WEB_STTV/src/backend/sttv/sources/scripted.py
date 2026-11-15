"""Read named libraries separately from independently selected game documents."""

from sttv.script.inline import Expansion
from sttv.script.parser import parse_text
from sttv.script.scripted.index import Index
from .files import read_source, source_files


def load_library(settings, report, variables, templates):
    library = Index(settings.scripted_options)
    library.value_options = settings.value_options
    report.data['counts']['scripted_calls'] = library.counts
    preparer = Expansion(templates, settings.inline_options, report, variables=variables)
    preparer.preparing = True
    for kind, directory, manifest in (
        ('scripted_effect', settings.scripted_effects_directory, 'scripted_effect_sources'),
        ('scripted_trigger', settings.scripted_triggers_directory, 'scripted_trigger_sources'),
        ('script_value', settings.script_values_directory, 'script_value_sources'),
    ):
        seen = set()
        options = settings.scripted_options
        for path in source_files(directory, options['pattern'], options['recursive']):
            stat = path.stat()
            identity = (stat.st_dev, stat.st_ino)
            if identity in seen:
                continue
            seen.add(identity)
            relative = path.relative_to(settings.game).as_posix()
            text = read_source(path, options['encoding'], report, relative, manifest)
            document = parse_text(text, settings.syntax, relative, role='template')
            preparer.expand(document, settings.syntax, root_only=True)
            # Index root insertions with their actual generated source, not caller offsets.
            object.__setattr__(document, 'node_sources', dict(preparer.sources))
            library.add(document, kind, settings.syntax, variables)
    report.data['library_fields'] = library.file_fields
    report.data['counts']['scripted_calls'] = library.counts
    return library

"""Create operation-scoped expansion contexts and filter template input roots."""

from sttv.script.inline import Expansion, FileTemplates


def expansion_context(settings, report=None):
    return Expansion(FileTemplates(settings.inline_directory, settings.inline_options),
                     settings.inline_options, report)


def independent_sources(paths, settings):
    for path in paths:
        if not path.resolve().is_relative_to(settings.inline_directory):
            yield path

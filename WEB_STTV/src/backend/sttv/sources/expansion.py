"""Create expansion contexts and exclude definition libraries from input roots."""

from sttv.script.inline import Expansion, FileTemplates


def expansion_context(settings, report=None):
    return Expansion(FileTemplates(settings.inline_directory, settings.inline_options,
                                   settings.parser_exceptions['inline_script_files']),
                     settings.inline_options, report)


def source_exclusion(path, settings):
    resolved = path.resolve()
    for variable, directory in (("INLINE_SCRIPTS_DIR", settings.inline_directory),
                                ("SCRIPTED_EFFECTS_DIR", settings.scripted_effects_directory)):
        if resolved.is_relative_to(directory):
            return variable
    return None


def independent_sources(paths, settings):
    for path in paths:
        if source_exclusion(path, settings) is None:
            yield path

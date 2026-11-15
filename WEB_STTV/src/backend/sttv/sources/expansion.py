"""Create expansion contexts and exclude definition libraries from input roots."""

from sttv.script.inline import Expansion, FileTemplates


def expansion_context(settings, report=None, variables=None):
    from sttv.common.report import Report
    from .static_variables import variable_processor
    from .scripted import load_library
    report = report if report is not None else Report()
    variables = variables or variable_processor(settings, report)
    templates = FileTemplates(settings.inline_directory, settings.inline_options,
                              settings.parser_exceptions['inline_script_files'])
    library = load_library(settings, report, variables, templates)
    return Expansion(templates, settings.inline_options, report, library, variables)


def source_exclusion(path, settings):
    resolved = path.resolve()
    for variable, directory in (("INLINE_SCRIPTS_DIR", settings.inline_directory),
                                ("SCRIPTED_EFFECTS_DIR", settings.scripted_effects_directory),
                                ("SCRIPTED_TRIGGERS_DIR", settings.scripted_triggers_directory),
                                ("SCRIPTED_VARIABLES_DIR", settings.scripted_variables_directory),
                                ("SCRIPT_VALUES_DIR", settings.script_values_directory)):
        if resolved.is_relative_to(directory):
            return variable
    return None


def independent_sources(paths, settings):
    for path in paths:
        if source_exclusion(path, settings) is None:
            yield path

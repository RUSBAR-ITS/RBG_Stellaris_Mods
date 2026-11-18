"""Create expansion contexts and exclude definition libraries from input roots."""

from sttv.script.inline import Expansion, FileTemplates


def expansion_context(settings, report=None, variables=None):
    from sttv.common.report import Report
    from .static_variables import variable_processor
    from sttv.libraries.operation import current
    from sttv.script.source_exceptions import SourceExceptions
    report = report if report is not None else Report()
    variables = variables or variable_processor(settings, report)
    templates, library = current(settings).context(settings, report)
    corrections = SourceExceptions(settings.source_exceptions, report, settings.source_exceptions_file,
                                    settings.inline_directory.relative_to(settings.game).as_posix())
    return Expansion(templates, settings.inline_options, report, library, variables, corrections)


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

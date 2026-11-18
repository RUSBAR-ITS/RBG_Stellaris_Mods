"""Derive individual parser settings and validate every destination together."""

from sttv.common.paths import distinct_paths, output_path, selected_path
from sttv.common.schema import validate_schema
from sttv.sources.settings import load_settings
from sttv.common.datasets import KINDS, REGISTRY, REGISTRY_PATH


def build_options(options, kind):
    dataset = options['datasets'][kind]
    return {'parser': options['parser'], 'libraries': options['libraries'], 'parallel': options['parallel'], 'sources': dataset['sources'],
            'outputs': {key: dataset['outputs'][key] for key in ('database', 'report')}}


def configure(variables_path, config_path, options):
    validate_schema(REGISTRY, 'datasets.schema.json')
    validate_schema(options, 'database_set.schema.json')
    settings = {kind: load_settings(variables_path, config_path, build_options(options, kind))
                for kind in KINDS}
    first = settings[KINDS[0]]
    first.config_files.append(REGISTRY_PATH)
    localization = selected_path(options['localization'], first.work)
    aggregate = output_path(first.work, options['report'], first.protected)
    paths = [aggregate, localization, *first.config_files]
    paths.extend(output_path(first.work, row['output'], first.protected)
                 for row in first.libraries['libraries'])
    paths.extend(output_path(first.work, first.libraries[key], first.protected)
                 for key in ('manifest', 'report'))
    for kind, item in settings.items():
        paths.extend([item.database, item.report, output_path(item.work,
            options['datasets'][kind]['outputs']['localization_report'], item.protected)])
    distinct_paths(paths)
    for item in settings.values():
        directory = item.parallel['directory']
        if any(path.resolve().is_relative_to(directory) or directory.is_relative_to(path.resolve()) for path in paths):
            from sttv.common.errors import BuildError
            raise BuildError('parallel_path_collision', 'Staging overlaps database-set inputs or outputs')
    existing = [path for path in paths if path.exists()]
    if any(left.samefile(right) for i, left in enumerate(existing) for right in existing[i + 1:]):
        from sttv.common.errors import BuildError
        raise BuildError('output_collision', 'Database-set paths alias each other')
    return settings, localization, aggregate

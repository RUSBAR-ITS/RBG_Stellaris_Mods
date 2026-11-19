"""Publish only after every localized member has been prepared and validated."""

from pathlib import Path
from time import perf_counter

from sttv.common.paths import PRODUCT_ROOT, output_path, selected_path
from sttv.common.persistence import save_json
from sttv.common.report import Report
from sttv.enrichment.localization.report import new_report, failure
from .configuration import KINDS, configure
from .inputs import Inputs
from .member import prepare_member
from sttv.storage.publication import Publication
from sttv.storage.settings import load as load_storage
from sttv.storage.manifest import create
from sttv.storage.identity import source_revision
from sttv.common.schema import schema_operation
from sttv.common.timing import performance, measure
from sttv.database.validation import database_rules
from contextlib import ExitStack
from sttv.libraries.operation import library_operation, require_mode
from sttv.parallel.pool import Pool


@schema_operation
def build_database_set(variables_path=None, config_path=None, *, library_mode=None):
    variables = Path(variables_path or PRODUCT_ROOT / 'global_variables.json')
    config = Path(config_path or PRODUCT_ROOT / 'config/backend.json')
    started, stage, current = perf_counter(), 'configuration', None
    report = {'format': 'sttv.database_set_report', 'format_version': 1, 'status': 'running',
              'set_id': None, 'snapshot_revision': None, 'published': False,
              'datasets': {}, 'diagnostics': [], 'inputs': [], 'seconds': 0.0,
              'performance': performance()}
    inputs, members = Inputs(report), {}
    settings, aggregate, builds, localizations = {}, None, {}, {}
    lifetime = ExitStack()
    try:
        require_mode(library_mode)
        rules = database_rules()
        report['performance']['timings']['prepare_rules'] = rules.seconds
        report['performance']['rule_preparations'] = 1
        inputs.record(variables, 'configuration')
        options = inputs.json(config, 'configuration')
        settings, localization, aggregate = configure(variables, config, options)
        storage = load_storage(variables, selected_path(options['storage'], settings[KINDS[0]].work))
        publication = lifetime.enter_context(Publication(storage))
        inputs.record(localization, 'configuration')
        for kind, item in settings.items():
            for path in item.config_files:
                inputs.record(path, 'configuration')
            inputs.capture_selection(item)
            outputs = options['datasets'][kind]['outputs']
            builds[kind], localizations[kind] = Report(), new_report()
            report['datasets'][kind] = {'database': str(item.database), 'build_report': str(item.report),
                'localization_report': str(output_path(item.work, outputs['localization_report'], item.protected)),
                'prepared': False, 'written': False, 'content_hash': None,
                'performance': builds[kind].data['performance'],
                'bytes': 0, 'seconds': 0.0,
                'build_status': 'not_started', 'localization_status': 'not_started',
                'build_counts': builds[kind].data['counts'], 'localization_counts': localizations[kind]['counts']}
        snapshot = lifetime.enter_context(library_operation(settings[KINDS[0]], library_mode))
        pool = lifetime.enter_context(Pool(settings[KINDS[0]], snapshot))
        for kind in KINDS:
            stage, current = 'preparation', kind
            member_started = perf_counter()
            members[kind] = prepare_member(kind, settings[kind], variables, localization,
                options['datasets'][kind]['outputs'], builds[kind], localizations[kind], inputs, publication, pool)
            report['datasets'][kind].update(prepared=True,
                content_hash=source_revision([r['descriptor'] for r in members[kind]]),
                bytes=sum(r['descriptor']['byte_size'] for r in members[kind]),
                seconds=round(perf_counter() - member_started, 3))
        pool.__exit__(None, None, None)
        stage, current = 'manifest', None
        with measure(report['performance']['timings'], 'manifest'):
            manifest = create(members)
        report['set_id'] = manifest['set_id']
        report['snapshot_revision'] = manifest['snapshot_revision']
        def verify():
            with measure(report['performance']['timings'], 'verify_inputs'):
                inputs.verify()
                snapshot.inventory.verify()
        stage = 'publication'
        with measure(report['performance']['timings'], 'publish'):
            report['published'] = publication.publish(manifest, verify)
        for member in report['datasets'].values():
            member['written'] = True
        report['status'] = 'success'
    except Exception as exc:
        report['status'] = 'failed'
        report['diagnostics'].append({'code': getattr(exc, 'code', 'set_build_error'),
                                      'stage': stage, 'message': str(exc), 'dataset': current,
                                      'node': getattr(exc, 'field_path', None)})
        if current in builds:
            if builds[current].data['status'] != 'success':
                builds[current].failure(exc, stage)
            else:
                failure(localizations[current], exc, stage)
                localizations[current]['status'] = 'failed'
    finally:
        try:
            lifetime.close()
        except Exception as exc:
            report['status'] = 'failed'
            report['diagnostics'].append({'code': 'library_report', 'stage': 'report',
                'message': str(exc), 'dataset': None, 'node': None})
    report['seconds'] = round(perf_counter() - started, 3)
    report['performance']['validated_documents'] = sum(
        member['performance']['validated_documents'] for member in report['datasets'].values())
    report['performance']['rule_preparations'] += sum(
        member['performance']['rule_preparations'] for member in report['datasets'].values())
    for kind, member in report['datasets'].items():
        member['build_status'] = ('failed' if builds[kind].failed else 'success'
            if builds[kind].data['status'] == 'success' else 'not_started')
        member['localization_status'] = ('not_started' if localizations[kind]['status'] == 'running'
                                         else localizations[kind]['status'])
        builds[kind].data['database_written'] = member['written']
        localizations[kind]['database_written'] = member['written']
        for path, value, schema in ((member['build_report'], builds[kind].data, 'report.schema.json'),
                (member['localization_report'], localizations[kind], 'localization_report.schema.json')):
            try:
                save_json(Path(path), value, schema)
            except Exception as exc:
                report['status'] = 'failed'
                report['diagnostics'].append({'code': 'report_write_failed', 'stage': 'report',
                    'message': str(exc), 'dataset': kind, 'node': None})
    if aggregate is not None:
        try:
            save_json(aggregate, report, 'database_set_report.schema.json')
        except Exception as exc:
            report['status'] = 'failed'
            report['diagnostics'].append({'code': 'report_write_failed', 'stage': 'report',
                'message': str(exc), 'dataset': None, 'node': None})
    return report

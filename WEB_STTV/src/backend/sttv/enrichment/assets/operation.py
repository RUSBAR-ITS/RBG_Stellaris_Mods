"""Enrich a prepared set without reparsing game scripts or changing tree inputs."""

from copy import deepcopy
from pathlib import Path
from time import perf_counter

from sttv.common.paths import PRODUCT_ROOT
from sttv.common.schema import schema_operation
from sttv.common.persistence import save_json
from sttv.common.timing import performance
from sttv.common.errors import BuildError
from sttv.storage import open_set
from sttv.storage.identity import digest
from sttv.storage.manifest import finalize
from sttv.storage.publication import Publication
from sttv.storage.writing import write_document
from sttv.storage.assets import verify_references
from sttv.enrichment.localization.snapshot import Snapshot
from .settings import configure
from .images import Images
from .selection import attach
from .categories import prepare_categories


@schema_operation
def prepare_assets(variables_path=None, config_path=None, *, storage_path=None):
    start = perf_counter()
    report = {'status': 'failed', 'inputs': [], 'duplicates': [], 'diagnostics': [], 'timings': {},
        'counts': dict.fromkeys(('technologies', 'variants', 'references', 'converted', 'reused',
                               'missing', 'image_bytes_written', 'documents_written'), 0)}
    snapshot, settings = Snapshot(report), None
    try:
        settings = configure(Path(variables_path or PRODUCT_ROOT / 'global_variables.json'),
            Path(config_path or PRODUCT_ROOT / 'config/enrichment/assets.json'), snapshot, storage_path)
        with Publication(settings.storage) as publication:
            reader = open_set(settings.storage.manifest)
            manifest = deepcopy(reader.manifest)
            report['before'] = manifest['snapshot_revision']
            images = Images(settings, publication, manifest.get('presentation', {}), snapshot, report)
            categories = set()
            started = perf_counter()
            for position, descriptor in enumerate(manifest['datasets']['technologies']['documents']):
                document = reader.read_document('technologies', descriptor['document_id'])
                changed = attach(document, settings, images, categories, report)
                for node in document['items']:
                    verify_references(node, {'files': images.files})
                if not changed:
                    continue
                fragment = write_document(document, publication.directory / f'{position}.json',
                                          'technologies', performance(), validate=False)
                if fragment['descriptor']['source_hash'] != descriptor['source_hash']:
                    raise BuildError('changed_source', 'Image enrichment changed technology source content')
                manifest['datasets']['technologies']['documents'][position] = publication.accept(fragment, 'technologies')['descriptor']
                report['counts']['documents_written'] += 1
            report['timings']['documents_and_images'] = perf_counter() - started
            icons = {area: images.get(path, {'resource': area}) for area, path in settings.options['research_icons'].items()}
            started = perf_counter()
            localized, index = prepare_categories(categories, settings, snapshot, report)
            report['timings']['localization'] = perf_counter() - started
            presentation = {'format_version': 1, 'settings_revision': images.revision,
                'files': images.files, 'sources': images.sources, 'research_icons': icons, 'categories': localized}
            presentation['revision'] = digest(presentation)
            manifest['presentation'] = presentation
            finalize(manifest)
            if manifest['set_id'] != reader.manifest['set_id']:
                raise BuildError('changed_source', 'Resource preparation changed the source set identity')
            def verify():
                reader.check_snapshot()
                snapshot.verify()
                index.verify_files()
            report['published'] = publication.publish(manifest, verify)
            report.update(status='success', after=manifest['snapshot_revision'], coverage=reader.coverage())
            report['counts'].update(unique_images=len(images.files), categories=len(categories),
                image_bytes=sum(row['byte_size'] for row in images.files.values()))
    except Exception as exc:
        report['diagnostics'].append({'severity': 'error', 'code': getattr(exc, 'code', 'assets_failed'),
                                      'message': str(exc), 'details': getattr(exc, 'context', {})})
    report['timings']['total'] = perf_counter() - start
    if settings:
        try:
            save_json(settings.report, report, 'assets_report.schema.json')
        except Exception as exc:
            report['status'] = 'failed'
            report['diagnostics'].append({'severity': 'error', 'code': 'report_write_failed', 'message': str(exc)})
    return report

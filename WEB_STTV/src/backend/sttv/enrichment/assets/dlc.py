"""Prepare descriptor thumbnails through the existing image pipeline."""

from pathlib import PurePosixPath

from sttv.common.errors import BuildError
from sttv.storage.settings import confined
from sttv.enrichment.technology_tree.ast import scalar


def prepare(reader, settings, images, report):
    result, documents = {}, {}
    def document(identifier):
        if identifier not in documents:
            documents[identifier] = reader.read_document('dlcs', identifier)
        return documents[identifier]
    for row in reader.iter_objects('dlcs'):
        node = document(row['document_id'])
        for part in row['pointer'].strip('/').split('/'):
            node = node[int(part)] if isinstance(node, list) else node[part]
        refs = node.get('enrichments', {}).get('dlc', {}).get('descriptors', [])
        paths = set()
        for ref in refs:
            descriptor = document(ref['document_id'])
            thumbnail = scalar(descriptor, settings.options['dlc_thumbnails']['field'])
            if thumbnail:
                directory = PurePosixPath(descriptor['source']['file']).parent
                # Validate both the source-relative field and the resolved DLC confinement.
                base = confined(settings.source, directory.as_posix())
                target = confined(base, thumbnail.replace('\\', '/'))
                if not target.is_relative_to(settings.dlc_root):
                    raise BuildError('unsafe_thumbnail', 'DLC thumbnail leaves the configured DLC directory')
                paths.add(target.relative_to(settings.source).as_posix())
        if len(paths) > 1:
            raise BuildError('dlc_thumbnail_conflict', f'Multiple thumbnails for {row["id"]}')
        result[row['id']] = images.get(next(iter(paths)), {'dlc': row['id']}) if paths else None
        if not paths:
            report['diagnostics'].append({'severity': 'warning', 'code': 'dlc_thumbnail_missing', 'dlc': row['id']})
    report['counts']['dlc_images'] = sum(value is not None for value in result.values())
    return result

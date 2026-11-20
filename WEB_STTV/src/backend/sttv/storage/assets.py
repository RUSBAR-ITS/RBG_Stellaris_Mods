"""Verify declared resources independently of game installation paths."""

from sttv.common.errors import BuildError
from .identity import digest, relative
from .settings import confined
from .publication import file_digest


def check_assets(manifest, paths):
    presentation = manifest.get('presentation')
    if presentation is None:
        return
    if presentation['revision'] != digest({k: v for k, v in presentation.items() if k != 'revision'}):
        raise BuildError('asset_revision', 'Presentation revision does not match content')
    for identifier, row in presentation['files'].items():
        path = relative(row['path']).casefold()
        if identifier != row['file_hash'] or path in paths:
            raise BuildError('asset_identity', 'Duplicate resource path or invalid resource identity')
        paths.add(path)
    for identifier in [*presentation['research_icons'].values(),
                       *presentation.get('dlc_icons', {}).values(),
                       *(row['asset_id'] for row in presentation['sources'].values())]:
        if identifier is not None and identifier not in presentation['files']:
            raise BuildError('missing_asset', 'Resource reference is not in the manifest')


def verify_asset(root, descriptor):
    from PIL import Image
    path = confined(root, descriptor['path'])
    if (not path.is_file() or path.stat().st_size != descriptor['byte_size']
            or file_digest(path) != descriptor['file_hash']):
        raise BuildError('asset_hash', f'Missing or corrupt resource: {descriptor["path"]}')
    with Image.open(path) as image:
        if image.format != 'PNG' or image.size != (descriptor['width'], descriptor['height']):
            raise BuildError('asset_dimensions', f'Invalid resource image: {descriptor["path"]}')
        image.verify()


def verify_references(node, presentation):
    """Inspect only presentation slots at the technology and direct variant levels."""
    for item in (node, *node.get('value', {}).get('items', [])):
        value = item.get('enrichments', {}).get('presentation')
        if value is None:
            continue
        identifier = value.get('icon_asset_id')
        if (value.get('format_version') != 1 or 'icon_asset_id' not in value
                or identifier is not None and identifier not in presentation['files']):
            error = BuildError('missing_asset', 'Invalid prepared image reference')
            error.context = {'asset_id': identifier}
            raise error

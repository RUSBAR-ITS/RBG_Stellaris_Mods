"""Select game images and prepare game-relative PNGs on the workstation."""

from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from tempfile import NamedTemporaryFile
import shutil

from document_package.json_io import read_json


def relative(value):
    if not isinstance(value, str) or not value:
        raise ValueError(f'Expected a relative path: {value!r}')
    path = PureWindowsPath(value)
    if path.anchor or '..' in path.parts or not path.parts or ':' in value:
        raise ValueError(f'Expected a confined relative path: {value!r}')
    return Path(*path.parts)


def confined(root, path):
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Path outside permitted directory: {path}')
    return path


@dataclass(frozen=True)
class Source:
    group: str
    file: Path
    name: str
    descriptor: str = ''


def group_files(directory, options):
    if 'pattern' in options:
        pattern = options['pattern']
        if '/' in pattern or '\\' in pattern or '**' in pattern:
            raise ValueError(f'Expected a nonrecursive filename pattern: {pattern}')
        for file in sorted(directory.glob(pattern)):
            if file.is_file():
                yield file
    else:
        for name in options['files']:
            yield directory / relative(name)


def thumbnails(game, directory, documents, field):
    if not documents.is_dir():
        raise ValueError(f'Missing descriptor directory: {documents}')
    for file in sorted(documents.rglob('*.json')):
        doc = read_json(confined(documents, file))
        name = doc['source']['file']
        try:
            descriptor = confined(directory, game / relative(name))
            values = [node['value'] for node in doc['items']
                      if node.get('kind') == 'assignment' and node['key'].get('text') == field]
            if not values:
                continue
            if len(values) != 1 or values[0].get('kind') != 'scalar':
                raise ValueError(f'Expected one scalar {field}')
            path = descriptor.parent / relative(values[0]['text'])
            yield confined(descriptor.parent, path), name
        except ValueError as exc:
            raise ValueError(f'{name}: {exc}') from exc


def select_images(game, documents, groups):
    selected = {}
    for group, rule in groups.items():
        directory = confined(game, game / relative(rule['directory']))
        if not directory.is_dir():
            raise ValueError(f'Missing image directory: {rule["directory"]}')
        if 'descriptor_field' in rule:
            entries = thumbnails(game, directory, documents, rule['descriptor_field'])
        else:
            entries = ((file, '') for file in group_files(directory, rule))
        for file, descriptor in entries:
            confined(directory, file)
            name = file.relative_to(game).as_posix()
            if not file.is_file() or file.suffix.lower() not in ('.dds', '.png'):
                raise ValueError(f'{descriptor or group}: missing or unsupported image {name}')
            target = file.relative_to(game).with_suffix('.png').as_posix()
            if target in selected and selected[target].file != file:
                raise ValueError(f'Output collision at {target}: {selected[target].name} and {name}')
            selected[target] = Source(group, file, name, descriptor)
    return selected


def prepare_png(source, target):
    from PIL import Image

    target.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=target.parent, delete=False) as temp:
        temporary = Path(temp.name)
    try:
        with Image.open(source.file) as image:
            # The vanilla Overlord descriptor names a JPEG thumbnail "thumbnail.png".
            mislabeled_thumbnail = source.descriptor and source.file.suffix.lower() == '.png' and image.format == 'JPEG'
            if image.format != source.file.suffix[1:].upper() and not mislabeled_thumbnail:
                raise ValueError('Image format and extension differ')
            if image.format == 'PNG':
                image.verify()
                shutil.copyfile(source.file, temporary)
            else:
                with image.convert('RGBA') as rgba:
                    rgba.save(temporary, format='PNG', compress_level=6)
        temporary.replace(target)
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError, NotImplementedError) as exc:
        raise ValueError(f'{source.descriptor or source.group}: {source.name}: {exc}') from exc
    finally:
        temporary.unlink(missing_ok=True)

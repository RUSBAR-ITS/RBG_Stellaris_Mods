"""Read localized DLC titles and descriptor-relative image paths from MongoDB."""

from pathlib import PureWindowsPath

from ..localization import determine_key, lookup
from .ast import scalar
from .errors import BuildError
from .inputs import records


def thumbnails(database):
    paths = {}
    for row in database['dlc_descriptors'].find({}, {'source.file': 1, 'tree': 1}):
        body = {'items': row['tree']}
        name, image = scalar(body, 'name'), scalar(body, 'thumbnail')
        if not image:
            continue
        source, relative = PureWindowsPath(row['source']['file']), PureWindowsPath(image)
        if (source.anchor or not source.parts or source.parts[0] != 'dlc' or relative.anchor
                or not relative.parts or '..' in (*source.parts, *relative.parts) or ':' in image):
            raise BuildError('invalid_thumbnail', f'Invalid DLC thumbnail path in {source}')
        if name in paths:
            raise BuildError('duplicate_descriptor', f'Multiple thumbnails for {name}')
        paths[name] = (source.parent / relative).with_suffix('.png').as_posix()
    return paths


def catalog(database, key_rules, read_strings):
    images = thumbnails(database)
    entries = []
    for row in sorted(records(database, 'dlcs', ['name', 'localizable_name']), key=lambda r: r['id']):
        entries.append((row['id'], scalar(row['body'], 'name'), scalar(row['body'], 'localizable_name'),
                        determine_key(key_rules, 'dlc_project_name', row['id'])))
    game = {key for _, _, key, _ in entries if key}
    project = {key for _, _, _, key in entries if key}

    def translations(language, keys):
        return {i['key']: i['text'] for i in lookup(language, sorted(keys), read_strings)['items']}

    ru, en = translations('ru', game | project), translations('en', game)
    return {'items': [{'id': identifier, 'thumbnail': images.get(name),
                       'name': {'ru': ru.get(project_key) or ru.get(game_key) or name,
                                'en': en.get(game_key) or name}}
                      for identifier, name, game_key, project_key in entries]}

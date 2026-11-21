"""Image preparation checks and an opt-in SSH interruption test on a writable test VM."""

import hashlib
import io
import json
import os
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory, TemporaryFile
import unittest
from uuid import uuid4

from sttv_loader.__main__ import run
from sttv_loader.image_sources import prepare_png, select_images
from sttv_loader.image_ssh import ssh_receiver

try:
    from PIL import Image
except ImportError:
    Image = None


def picture(path, color, fmt='PNG'):
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = 'RGB' if fmt == 'JPEG' else 'RGBA'
    with Image.new(mode, (4, 2), color) as image:
        image.save(path, format=fmt)


@unittest.skipUnless(Image, 'Requires the loader images extra')
class ImageSelectionTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.game = self.root / 'game'
        self.docs = self.root / 'descriptors'
        self.docs.mkdir()
        self.groups = {
            'tech': {'directory': 'gfx/tech', 'pattern': '*.dds'},
            'categories': {'directory': 'gfx/tech/categories', 'pattern': 'category_*.dds'},
            'research': {'directory': 'gfx/resources', 'files': ['physics.dds']},
            'dlc': {'directory': 'dlc', 'descriptor_field': 'thumbnail'},
        }
        for name in ('tech/icon', 'tech/old/old', 'tech/categories/category_one',
                     'tech/categories/unused', 'resources/physics', 'resources/unused'):
            picture(self.game / 'gfx' / (name + '.dds'), (11, 22, 33, 47), 'DDS')
        for pack, color in [('one', 'red'), ('two', 'blue')]:
            picture(self.game / 'dlc' / pack / 'thumbnail.png', color)
            self.descriptor(pack, 'thumbnail.png')
        self.descriptor('empty', None)

    def descriptor(self, pack, value):
        items = [] if value is None else [
            {'kind': 'assignment', 'key': {'text': 'thumbnail'},
             'value': {'kind': 'scalar', 'text': value}}]
        document = {'source': {'file': f'dlc/{pack}/pack.dlc'}, 'items': items}
        (self.docs / (pack + '.json')).write_text(json.dumps(document), encoding='utf-8')

    def select(self):
        return select_images(self.game, self.docs, self.groups)

    def test_game_relative_paths_pixels_and_png_bytes(self):
        images = self.select()
        self.assertEqual(set(images), {'gfx/tech/icon.png', 'gfx/tech/categories/category_one.png',
                                      'gfx/resources/physics.png', 'dlc/one/thumbnail.png',
                                      'dlc/two/thumbnail.png'})
        for name, source in images.items():
            target = self.root / 'output' / name
            prepare_png(source, target)
            with Image.open(target) as result:
                self.assertEqual((result.format, result.size), ('PNG', (4, 2)))
                if source.file.suffix == '.dds':
                    self.assertEqual(result.getpixel((0, 0)), (11, 22, 33, 47))
                else:
                    self.assertEqual(target.read_bytes(), source.file.read_bytes())

    def test_jpeg_declared_as_dlc_png(self):
        file = self.game / 'dlc/one/thumbnail.png'
        picture(file, 'red', 'JPEG')
        target = self.root / 'out.png'
        prepare_png(self.select()['dlc/one/thumbnail.png'], target)
        with Image.open(file) as original, Image.open(target) as result:
            self.assertEqual(result.format, 'PNG')
            self.assertEqual(result.size, original.size)
            self.assertEqual(result.convert('RGB').tobytes(), original.tobytes())

    def test_declared_missing_thumbnail(self):
        self.descriptor('one', 'missing.png')
        with self.assertRaisesRegex(ValueError, 'dlc/one/pack.dlc.*dlc/one/missing.png'):
            self.select()

    def test_corrupt_png_reports_source_and_keeps_previous_output(self):
        source = self.select()['dlc/one/thumbnail.png']
        target = self.root / 'out.png'
        prepare_png(source, target)
        previous = target.read_bytes()
        broken = bytearray(previous)
        broken[broken.index(b'IDAT') + 4] ^= 1
        source.file.write_bytes(broken)
        with self.assertRaisesRegex(ValueError, 'dlc/one/pack.dlc.*dlc/one/thumbnail.png'):
            prepare_png(source, target)
        self.assertEqual(target.read_bytes(), previous)

    def test_thumbnail_cannot_escape_its_dlc(self):
        for name in ('../two/thumbnail.png', '/outside.png', 'C:/outside.png'):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'dlc/one/pack.dlc'):
                self.descriptor('one', name)
                self.select()

    def test_collision_detected_at_selection(self):
        picture(self.game / 'gfx/resources/physics.png', 'green')
        self.groups['research']['files'].append('physics.png')
        with self.assertRaisesRegex(ValueError, 'Output collision.*physics.png'):
            self.select()


@unittest.skipUnless(Image and os.environ.get('STTV_IMAGE_TEST_CONFIG'),
                     'Requires Pillow and a dedicated writable SSH test destination')
class ImageSshTests(unittest.TestCase):
    def test_single_change_interrupted_replacement_and_retry(self):
        config = Path(os.environ['STTV_IMAGE_TEST_CONFIG']).resolve()
        options = json.loads(config.read_text(encoding='utf-8-sig'))
        scratch = (config.parent / options['run_directory'] / 'artifacts').resolve()
        scratch.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(dir=scratch) as temp:
            work = Path(temp)
            group = 'test-' + uuid4().hex
            game = work / 'game'
            first = game / group / 'one.png'
            second = first.with_name('two.png')
            picture(first, 'red')
            picture(second, 'blue')
            options.update(game_root=str(game), descriptor_directory=str(game / 'dlc'),
                           run_directory=str(work / 'run'),
                           groups={'icons': {'directory': group, 'files': ['one.png', 'two.png']}})
            for setting in ('executable', 'known_hosts'):
                options['ssh'][setting] = str((config.parent / options['ssh'][setting]).resolve())
            active = work / 'upload.json'
            active.write_text(json.dumps(options), encoding='utf-8')
            self.assertEqual(run('upload-images', active)['groups']['icons']['transferred'], 2)
            picture(first, 'yellow')
            counts = run('upload-images', active)['groups']['icons']
            self.assertEqual(counts, {'selected': 2, 'transferred': 1, 'skipped': 1})
            previous = hashlib.sha256(first.read_bytes()).hexdigest()
            picture(first, 'green')
            updated = first.read_bytes()
            name = first.relative_to(game).as_posix()
            other = second.relative_to(game).as_posix()
            query = json.dumps([name, other]).encode()
            with ssh_receiver(config.parent, options['ssh'], work, options['destination_root']) as execute:
                buffer = io.BytesIO()
                with tarfile.open(fileobj=buffer, mode='w') as archive:
                    item = tarfile.TarInfo(name)
                    item.size = len(updated)
                    item.pax_headers['STTV.sha256'] = hashlib.sha256(updated).hexdigest()
                    archive.addfile(item, io.BytesIO(updated))
                buffer.seek(0)
                with tarfile.open(fileobj=buffer) as archive:
                    cutoff = archive.getmember(name).offset_data + len(updated) // 2
                with TemporaryFile(dir=work) as stream:
                    stream.write(buffer.getvalue()[:cutoff])
                    stream.seek(0)
                    interrupted = execute('publish', stream=stream)
                self.assertNotEqual(interrupted.returncode, 0)
                self.assertIn(name, interrupted.stderr.decode())
                hashes = json.loads(execute('hashes', payload=query).stdout)
                self.assertEqual(hashes[name], previous)
                self.assertEqual(hashes[other], hashlib.sha256(second.read_bytes()).hexdigest())
                options['groups']['icons']['files'] = ['one.png']
                active.write_text(json.dumps(options), encoding='utf-8')
                self.assertEqual(run('upload-images', active)['groups']['icons'],
                                 {'selected': 1, 'transferred': 1, 'skipped': 0})
                after = json.loads(execute('hashes', payload=query).stdout)
                self.assertEqual(after[name], hashlib.sha256(updated).hexdigest())
                self.assertEqual(after[other], hashes[other])

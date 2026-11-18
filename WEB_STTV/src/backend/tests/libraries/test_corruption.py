"""Reject malformed service records, references and interrupted generations."""

import hashlib
import json

from sttv.common.errors import BuildError
from sttv.common.schema import validate_schema
from sttv.libraries.inventory import digest
from sttv.libraries.validation import artifact_validator
from .fixture import LibraryFixture


class CorruptionTests(LibraryFixture):
    def change_artifact(self, edit):
        manifest = json.loads(self.manifest().read_text(encoding='utf-8'))
        row = next(row for row in manifest['artifacts'] if row['kind'] == 'inline_script')
        path = self.manifest().parent.parent/row['path']
        value = json.loads(path.read_text(encoding='utf-8'))
        edit(value)
        path.write_text(json.dumps(value), encoding='utf-8')
        row['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest['library_set_id'] = digest({row['kind']: row['sha256'] for row in manifest['artifacts']})
        self.manifest().write_text(json.dumps(manifest), encoding='utf-8')

    def test_missing_corrupt_and_unknown_manifest(self):
        with self.assertRaises(BuildError) as error:
            self.prepare('reuse')
        self.assertEqual(error.exception.code, 'library_missing')
        self.prepare()
        self.manifest().write_text('{', encoding='utf-8')
        with self.assertRaises(BuildError) as error:
            self.prepare('reuse')
        self.assertEqual(error.exception.code, 'library_corrupt')
        self.prepare()
        value = json.loads(self.manifest().read_text(encoding='utf-8'))
        value['preparation_version'] = 'future'
        self.manifest().write_text(json.dumps(value), encoding='utf-8')
        with self.assertRaises(BuildError) as error:
            self.prepare('reuse')
        self.assertEqual(error.exception.code, 'library_version')

    def test_missing_artifact_and_hash_mismatch(self):
        self.prepare()
        self.artifacts()[-1].unlink()
        with self.assertRaises(BuildError) as error:
            self.prepare('reuse')
        self.assertEqual(error.exception.code, 'library_missing')
        self.prepare()
        path = self.artifacts()[-1]
        path.write_bytes(path.read_bytes() + b' ')
        with self.assertRaises(BuildError) as error:
            self.prepare('reuse')
        self.assertEqual(error.exception.code, 'library_checksum')

    def test_bad_internal_reference_and_plan_are_rejected(self):
        self.prepare()
        self.change_artifact(lambda value: value['graph'].update(root={'$ref': 99999999}))
        with self.assertRaises(BuildError) as error:
            self.prepare('reuse')
        self.assertEqual(error.exception.code, 'library_reference')
        self.prepare()

        def damage(value):
            source = next(row for row in value['graph']['objects'] if row['type'] == 'Source')
            source['fields']['plan']['tokens'][0]['end'] = 99999999
        self.change_artifact(damage)
        with self.assertRaises(BuildError) as error:
            self.prepare('reuse')
        self.assertEqual(error.exception.code, 'library_plan')

    def test_fast_schema_check_agrees_with_json_schema(self):
        self.prepare()
        check = artifact_validator()
        for path in self.artifacts()[1:]:
            value = json.loads(path.read_text(encoding='utf-8'))
            validate_schema(value, 'library.schema.json')
            check(value)
            value['extra'] = True
            with self.assertRaises(BuildError):
                validate_schema(value, 'library.schema.json')
            with self.assertRaises(BuildError):
                check(value)

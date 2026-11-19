"""Substitution after nested expansion without replacement metadata or scope leaks."""

from copy import deepcopy

from support import BuildFixture
from sttv.database.history import validate_history
from sttv.script.parser import parse_text
from sttv.script.serialization import serialize_document
from sttv.sources.settings import load_settings
from sttv.sources.expansion import expansion_context


class StaticBuildTests(BuildFixture):
    def test_nested_arguments_origin_history_and_document_isolation(self):
        self.write_script('base.txt', '@cost=3 box={inline_script={script=outer VALUE=@cost}}')
        self.write_script('second.txt', '@cost=7 second_box={inline_script={script=outer VALUE=@cost}}')
        (self.inline / 'outer.txt').write_text('inline_script={script=inner VALUE=$VALUE$}', encoding='utf-8')
        (self.inline / 'inner.txt').write_text('amount=$VALUE$ quoted="$VALUE$"', encoding='utf-8')
        result = self.run_build()
        self.assertEqual(result['status'], 'success', result)
        self.assertEqual(result['counts']['static_variables']['substituted'], 2)
        settings = load_settings(self.variable_file, self.config_file)
        from sttv.libraries.operation import library_operation
        with library_operation(settings, 'reuse'):
            context = expansion_context(settings)
        for document in self.database()['documents']:
            file = document['source']['file']
            if not file.endswith(('base.txt', 'second.txt')) or '/category/' in file or '/tier/' in file:
                continue
            raw = parse_text((self.game / file).read_text(encoding='utf-8-sig'), settings.syntax,
                             file, expansion=context)
            expected = serialize_document(raw)
            amount = document['items'][1]['value']['items'][0]['value']
            expected['items'][1]['value']['items'][0]['value'].update(
                raw='3' if file.endswith('/base.txt') else '7',
                text='3' if file.endswith('/base.txt') else '7')
            self.assertEqual({k: document[k] for k in ('source', 'items', 'metadata')}, expected)
            self.assertEqual(document['items'][1]['value']['items'][1]['value']['text'], '@cost')
            self.assertEqual(document['metadata']['expansions'][0]['arguments'][0]['value'], '@cost')
            self.assertIsNotNone(amount['origin']['expansion_id'])
            validate_history(document)

    def test_inline_declarations_and_failure_preserve_previous_database(self):
        self.write_script('base.txt', 'inline_script=definitions value=@inserted')
        (self.inline / 'definitions.txt').write_text('@inserted=9', encoding='utf-8')
        self.assertEqual(self.run_build()['status'], 'success')
        self.assertEqual(self.database()['documents'][0]['items'][1]['value']['text'], '9')
        before = self.database_path().read_bytes()
        for source, code in [('box={inline_script=definitions}', 'nested_static_declaration'),
                             ('value=@missing', 'unknown_static_variable')]:
            self.write_script('base.txt', source)
            result = self.run_build()
            self.assertIn(code, self.errors(result))
            self.assertFalse(result['database_written'])
            self.assertEqual(before, self.database_path().read_bytes())

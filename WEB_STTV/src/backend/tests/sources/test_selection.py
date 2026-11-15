"""Source selection, physical-file deduplication, and output boundaries."""

from copy import deepcopy
import os

from support import BuildFixture, PRODUCT_ROOT


class SelectionTests(BuildFixture):
    def test_overlapping_selections_and_hardlinks_are_read_once(self):
        self.options['sources'].append(deepcopy(self.options['sources'][0]))
        os.link(self.tech / 'base.txt', self.tech / 'duplicate.txt')
        result = self.run_build()
        self.assertEqual(result['status'], 'success', result)
        self.assertEqual(result['counts']['selected_files'], 3)
        self.assertEqual(len(self.database()['documents']), 3)
        self.options['sources'][1]['encoding'] = 'utf-16'
        self.assertIn('source_conflict', self.errors(self.run_build()))

    def test_empty_selection_fails_but_an_empty_file_is_saved(self):
        self.options['sources'][0]['pattern'] = 'absent_*.txt'
        self.assertIn('empty_sources', self.errors(self.run_build()))
        self.write_script('empty.txt', '# no definitions\n')
        self.options['sources'][0]['pattern'] = 'empty.txt'
        result = self.run_build()
        self.assertEqual(result['status'], 'success', result)
        self.assertEqual(self.database()['documents'][0]['items'], [])
        self.assertEqual(result['counts']['nodes'], 0)

    def test_source_and_output_escapes_are_rejected_without_writes(self):
        work = self.variables['WORK_DIR']
        for destination in (PRODUCT_ROOT.parent.parent / 'outside_stage6', PRODUCT_ROOT / 'src',
                            PRODUCT_ROOT / 'language', self.game.parent):
            self.variables['WORK_DIR'] = str(destination)
            self.assertIn('unsafe_output', self.errors(self.run_build()))
        self.variables['WORK_DIR'] = work
        self.variables['TECH_PATH'] = '../outside_game'
        self.assertIn('unsafe_source', self.errors(self.run_build()))
        self.assertFalse(self.database_path().exists())

    def test_encoding_errors_and_illegal_globs_are_reported(self):
        self.options['sources'][0]['encoding'] = 'nonexistent-encoding'
        result = self.run_build()
        self.assertIn('source_read_error', self.errors(result))
        self.assertEqual(result['counts']['failed_files'], 3)
        self.options['sources'][0]['pattern'] = '../*.txt'
        self.assertIn('invalid_pattern', self.errors(self.run_build()))

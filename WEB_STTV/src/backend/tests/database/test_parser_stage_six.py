"""Expansion integration without a profile or a technology projection."""

from support import BuildFixture


class ExpansionBuildTests(BuildFixture):
    def test_nested_expansion_history_and_template_updates(self):
        self.write_script('base.txt', 'box={ inline_script={script=outer V=alpha} inline_script=empty }')
        (self.inline / 'outer.txt').write_text('inline_script={script=inner V=$V$}', encoding='utf-8')
        (self.inline / 'inner.txt').write_text('future=$V$', encoding='utf-8')
        (self.inline / 'empty.txt').write_text('', encoding='utf-8')
        before = self.hashes()
        result = self.run_build()
        self.assertEqual(result['status'], 'success', result)
        self.assertEqual(result['counts']['inline_scripts']['expanded'], 3)
        doc = self.database()['documents'][0]
        self.assertEqual(doc['items'][0]['value']['items'][0]['value']['text'], 'alpha')
        self.assertEqual(doc['metadata']['inline_scripts'][1]['arguments'][0]['raw'], '$V$')
        self.assertEqual(before, self.hashes())
        (self.inline / 'inner.txt').write_text('changed=$V$', encoding='utf-8')
        self.assertEqual(self.run_build()['status'], 'success')
        self.assertEqual(self.database()['documents'][0]['items'][0]['value']['items'][0]['key']['text'], 'changed')

    def test_error_locations_and_source_chain_are_preserved(self):
        self.write_script('base.txt', 'inline_script=outer')
        (self.inline / 'outer.txt').write_text('AND={inline_script=inner}', encoding='utf-8')
        (self.inline / 'inner.txt').write_text('# comment\nx = =', encoding='utf-8')
        result = self.run_build()
        self.assertEqual(result['status'], 'failed')
        error = next(row for row in result['diagnostics'] if row['code'] == 'missing_value')
        self.assertEqual((error['source'], error['file'], error['line']), ('INLINE_SCRIPTS_DIR', 'inner.txt', 2))
        self.assertEqual([call['template'] for call in error['call_chain']], ['outer.txt', 'inner.txt'])
        self.assertEqual(error['root_source']['file'], 'common/technology/base.txt')
        self.assertFalse(result['database_written'])

    def test_unreachable_templates_are_excluded_from_independent_selection(self):
        self.variables['ALL_COMMON'] = 'common'
        self.options['sources'] = [{**self.options['sources'][0], 'variable': 'ALL_COMMON'}]
        (self.inline / 'unreachable.txt').write_text('inline_script=missing', encoding='utf-8')
        (self.inline / 'called.txt').write_text('future=yes', encoding='utf-8')
        self.write_script('base.txt', 'inline_script=called')
        result = self.run_build()
        self.assertEqual(result['status'], 'success', result)
        self.assertEqual(result['counts']['selected_files'], 3)
        self.assertEqual(set(result['inline_sources']), {'called.txt'})

    def test_failed_expansion_does_not_publish_partial_trees(self):
        self.assertEqual(self.run_build()['status'], 'success')
        before = self.database_path().read_bytes()
        for text, template in [('inline_script=missing', 'x=yes'),
                               ('inline_script=p', 'x=$MISSING$'),
                               ('inline_script=p', 'inline_script=p')]:
            self.write_script('base.txt', text)
            (self.inline / 'p.txt').write_text(template, encoding='utf-8')
            result = self.run_build()
            self.assertEqual(result['status'], 'failed')
            self.assertEqual(self.database_path().read_bytes(), before)

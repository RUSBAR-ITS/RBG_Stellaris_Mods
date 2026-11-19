"""End-to-end named expansion, logical boundaries, and lexical environments."""

from itertools import product

from support import BuildFixture


class ScriptedBuildTests(BuildFixture):
    def setup_calls(self, effects='', triggers='', caller=''):
        (self.effects / 'definitions.txt').write_text(effects, encoding='utf-8')
        (self.triggers / 'definitions.txt').write_text(triggers, encoding='utf-8')
        self.write_script('base.txt', caller)

    def document(self):
        report = self.run_build()
        self.assertEqual(report['status'], 'success', report['diagnostics'])
        return self.database()['documents'][0], report

    def test_mixed_chain_and_history_ranges(self):
        self.setup_calls('give={ inline_script={script=part VALUE=$VALUE$} }',
                         'ready={ a=yes b=yes }', 'before=0 give={VALUE=9} after=1')
        (self.inline / 'part.txt').write_text('amount=$VALUE$ ready=no', encoding='utf-8')
        doc, report = self.document()
        self.assertEqual([r['kind'] for r in doc['metadata']['expansions']],
                         ['scripted_effect', 'inline_script', 'scripted_trigger'])
        self.assertEqual([r['parent_id'] for r in doc['metadata']['expansions']],
                         [None, 'scripted_effect_1', 'inline_1'])
        self.assertEqual(doc['items'][1]['value']['text'], '9')
        self.assertEqual(doc['items'][2]['operator'], 'NOT')
        self.assertEqual(report['counts']['max_call_depth'], 3)

    def test_logical_truth_tables_preserve_whole_result(self):
        self.setup_calls(triggers='pair={ a=yes b=yes }',
                         caller='positive={OR={pair=yes c=yes}} negative={OR={pair=no c=yes}}')
        doc, _ = self.document()
        def evaluate(node, values):
            if node['kind'] == 'assignment':
                return values[node['key']['text']]
            items = node['body']['items']
            results = [evaluate(n, values) for n in items]
            if node['operator'] == 'AND':
                return all(results)
            if node['operator'] == 'OR':
                return any(results)
            return not all(results)
        for a, b, c in product((False, True), repeat=3):
            values = dict(a=a, b=b, c=c)
            self.assertEqual(evaluate(doc['items'][0]['value']['items'][0], values), (a and b) or c)
            self.assertEqual(evaluate(doc['items'][1]['value']['items'][0], values), not (a and b) or c)

    def test_nonboolean_tests_and_formulas_are_not_evaluated(self):
        self.setup_calls(triggers='population={ count_owned_pop_amount={} }',
                         caller='@threshold=200 box={population>@threshold population=ye population!=yes population>=@[2+1]}')
        doc, report = self.document()
        nodes = doc['items'][1]['value']['items']
        self.assertTrue(all(n['kind'] == 'scripted_trigger_test' for n in nodes))
        self.assertEqual([n['operator'] for n in nodes], ['>', '=', '!=', '>='])
        self.assertEqual(nodes[0]['value']['text'], '200')
        self.assertEqual(nodes[1]['value']['text'], 'ye')
        self.assertEqual(nodes[3]['value']['kind'], 'formula')
        self.assertEqual(report['counts']['scripted_calls']['scripted_trigger']['tests'], 4)

    def test_local_argument_default_and_inline_environments(self):
        self.setup_calls('@cost=20 give={ first=@cost second=$AMOUNT$ third=$DEFAULT|@cost$ '
                         'inline_script=literal other={ AMOUNT=$AMOUNT$ } }',
                         '@cost=30 other={ value=@cost argument=$AMOUNT$ }',
                         '@cost=10 give={AMOUNT=@cost}')
        (self.inline / 'literal.txt').write_text('fourth=@cost', encoding='utf-8')
        doc, _ = self.document()
        self.assertEqual([n['value']['text'] for n in doc['items'][1:5]], ['20', '10', '20', '20'])
        self.assertEqual([n['value']['text'] for n in doc['items'][5]['body']['items']], ['30', '10'])

    def test_defaults_conditional_forwarding_and_discarded_calls(self):
        self.setup_calls('outer={ [[ENABLED] inner={N=$N|7$} ] [[!ENABLED] result=$N|2$] '
                         '[[UNUSED] inline_script=missing required=$MISSING$] } inner={result=$N$}',
                         caller='@enabled=no outer={ENABLED=@enabled} outer={ENABLED=yes} outer={ENABLED=yes N=no}')
        doc, report = self.document()
        self.assertEqual([n['value']['text'] for n in doc['items'][1:]], ['2', '7', 'no'])
        self.assertEqual(report['counts']['parameters']['defaults'], 2)

    def test_block_and_formula_arguments_preserve_text(self):
        self.setup_calls('emit={ payload=$BLOCK$ amount=$VALUE$ }',
                         caller='emit={BLOCK={AND={x=yes}} VALUE=@[2+3]}')
        doc, _ = self.document()
        self.assertEqual(doc['items'][0]['value']['items'][0]['operator'], 'AND')
        self.assertEqual(doc['items'][1]['value']['raw'], '@[2+3]')

    def test_library_directives_and_unused_parameters(self):
        self.setup_calls('give={optimize_memory value=yes}', 'namespace=test ready={optimize_memory a=yes}',
                         'give={UNUSED=1} ready=yes')
        doc, report = self.document()
        self.assertEqual([r['directives'] for r in doc['metadata']['expansions']],
                         [['optimize_memory'], ['optimize_memory']])
        self.assertEqual(report['counts']['warnings'], 1)
        self.assertEqual(len(doc['items']), 2)

    def test_repeated_calls_do_not_share_results_and_empty_body(self):
        self.setup_calls('empty={} give={result=$VALUE$}', caller='empty=yes give={VALUE=1} give={VALUE=2}')
        doc, _ = self.document()
        self.assertEqual([n['value']['text'] for n in doc['items']], ['1', '2'])
        self.assertEqual([r['insertion']['count'] for r in doc['metadata']['expansions']], [0, 1, 1])

    def test_selected_and_inserted_directives_have_actual_history(self):
        self.setup_calls('give={[[ENABLED] optimize_memory] inline_script=marker value=yes}',
                         caller='give=yes give={ENABLED=yes}')
        (self.inline / 'marker.txt').write_text('optimize_memory', encoding='utf-8')
        doc, _ = self.document()
        self.assertEqual([r['directives'] for r in doc['metadata']['expansions']],
                         [['optimize_memory'], [], ['optimize_memory', 'optimize_memory'], []])
        self.assertEqual([r['insertion']['count'] for r in doc['metadata']['expansions']], [1, 0, 1, 0])
        self.assertEqual([n['key']['text'] for n in doc['items']], ['value', 'value'])

    def test_root_inline_declarations_and_library_definitions(self):
        self.setup_calls('inline_script=definitions', caller='inline_script=constants give=yes')
        (self.inline / 'definitions.txt').write_text('@cost=20 give={value=@cost}', encoding='utf-8')
        (self.inline / 'constants.txt').write_text('@cost=10', encoding='utf-8')
        doc, _ = self.document()
        self.assertEqual(doc['items'][1]['value']['text'], '20')

    def test_game_rule_definitions_and_inline_roots_preserve_nested_calls(self):
        self.setup_calls(triggers='same={value=$ARG$}', caller='same={ARG=9}')
        rules = self.game / 'common/game_rules'
        rules.mkdir()
        (rules / 'rules.txt').write_text('same={same={ARG=7}} inline_script=definition', encoding='utf-8')
        (self.inline / 'definition.txt').write_text('second={same={ARG=8}}', encoding='utf-8')
        self.variables['TECH_PATH'] = 'common/game_rules'
        doc, report = self.document()
        self.assertEqual(report['counts']['warnings'], 0)
        self.assertEqual([n['kind'] for n in doc['items']], ['assignment', 'assignment'])
        for node, expected in zip(doc['items'], ('7', '8')):
            inner = node['value']['items'][0]
            self.assertEqual(inner['operator'], 'AND')
            self.assertEqual(inner['body']['items'][0]['value']['text'], expected)
        self.variables['TECH_PATH'] = 'common/technology'
        doc, _ = self.document()
        self.assertEqual(doc['items'][0]['kind'], 'logical_operation')
        self.assertEqual(doc['items'][0]['body']['items'][0]['value']['text'], '9')

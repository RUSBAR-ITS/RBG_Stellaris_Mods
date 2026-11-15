"""Argument tokenization respects existing parameter delimiters."""

import unittest

from support import syntax
from sttv.script.nodes import Source
from sttv.script.values.references import candidate, invocation


class ValueReferenceTests(unittest.TestCase):
    def test_default_separator_does_not_split_a_parameter(self):
        options = dict(reference_prefix='value:', scope_separator='.', argument_separator='|')
        shared = dict(name_case_sensitive=False, parameter_case_sensitive=True)
        source = Source('value:target|MULT|$N|0$|')
        self.assertTrue(candidate(source, syntax(), options, False))
        name, scope, args, bindings = invocation(source, syntax(), options, shared)
        self.assertEqual(name, 'target')
        self.assertIsNone(scope)
        self.assertEqual(args[0]['value'], '$N|0$')
        self.assertEqual(bindings['MULT'].text, '$N|0$')

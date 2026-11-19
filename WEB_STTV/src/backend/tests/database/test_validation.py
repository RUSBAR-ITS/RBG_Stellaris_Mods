"""All syntax forms survive JSON; corrupted structural metadata is rejected."""

from copy import deepcopy
from dataclasses import asdict
import json
import unittest

from support import PRODUCT_ROOT, syntax
from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.database.validation import validate_database
from sttv.script.inline import Expansion, MemoryTemplates
from sttv.script.nodes import InlineInvocation, Span
from sttv.script.parser import parse_text
from sttv.script.serialization import encode, serialize_document, walk_nodes


def fixture(text, templates=None):
    options = read_json(PRODUCT_ROOT / "config/parser/inline_scripts.json")
    context = Expansion(MemoryTemplates(templates or {}, options), options)
    document = parse_text(text, syntax(), "fixture.txt", expansion=context)
    from sttv.storage.writing import prepare
    return prepare(serialize_document(document), "technologies"), document


class ValidationTests(unittest.TestCase):
    def test_every_node_kind_and_field_survives_json(self):
        text = 'bare @x=2 n=003.50 flag=yes key="$P|fallback$" x=@x x=@[ 1 + 2 ] '
        text += 'color=rgb { 1 2 3 } { inner=no } [[P] NOT={ a=b bare } ]'
        db, parsed = fixture(text)
        loaded = json.loads(json.dumps(db))
        validate_database(loaded)
        self.assertEqual(loaded, db)
        self.assertEqual({node["kind"] for _, node in walk_nodes(loaded["items"])},
                         {"scalar", "formula", "block", "tagged_block", "conditional", "assignment", "logical_operation"})
        for encoded, original in zip(loaded["items"], parsed.items):
            def json_form(value):
                return json.loads(json.dumps(value))
            self.assertEqual({k: v for k, v in encoded.items() if k != "kind" and k not in ("value", "items", "body", "key", "name")},
                         {k: json_form(v) for k, v in asdict(original).items() if k not in ("value", "items", "body", "key", "name", "environment")})
        parameters = loaded["items"][4]["value"]["parameters"]
        self.assertEqual(parameters[0]["default"], "fallback")

    def test_wrong_shapes_unknown_kinds_and_extra_fields_fail(self):
        db, _ = fixture('x=yes')
        mutations = [lambda d: d["items"][0].update(kind="unknown"),
                     lambda d: d["items"][0]["value"].update(text=True),
                     lambda d: d["items"][0].update(unknown="data"),
                     lambda d: d.update(items={}),
                     lambda d: d["items"][0]["key"].update(kind="block")]
        for mutate in mutations:
            damaged = deepcopy(db)
            mutate(damaged)
            with self.subTest(mutation=mutate), self.assertRaises(BuildError):
                validate_database(damaged)

    def test_nested_history_and_empty_ranges_are_preserved(self):
        db, _ = fixture('box={ inline_script=outer inline_script=empty }',
                        {'outer.txt': 'a=yes inline_script=inner', 'inner.txt': 'b=no', 'empty.txt': ''})
        validate_database(db)
        history = db["metadata"]["expansions"]
        self.assertEqual([c["insertion"]["count"] for c in history], [2, 1, 0])
        self.assertEqual(history[1]["parent_id"], history[0]["id"])
        self.assertEqual(history[0]["insertion"]["container"], "/items/0/value/items")
        mutations = [lambda h: h[1].update(id=h[0]["id"]),
                     lambda h: h[0].update(parent_id=h[1]["id"]),
                     lambda h: h[1].update(parent_id="missing"),
                     lambda h: h[0]["insertion"].update(index=999),
                     lambda h: h[0]["insertion"].update(count=-1),
                     lambda h: h[0]["insertion"].update(container="/metadata/inline_scripts"),
                     lambda h: h[1]["insertion"].update(index=0)]
        for mutate in mutations:
            damaged = deepcopy(db)
            mutate(damaged["metadata"]["expansions"])
            with self.subTest(mutation=mutate), self.assertRaises(BuildError):
                validate_database(damaged)
        damaged = deepcopy(db)
        damaged["items"][0]["origin"]["expansion_id"] = "missing"
        with self.assertRaises(BuildError):
            validate_database(damaged)

    def test_incompatible_database_and_unexpanded_invocation_are_explicit_errors(self):
        for value in ({"format_version": 2, "technologies": {}}, [], {"format": "sttv.parse_database", "format_version": 999}):
            with self.assertRaises(BuildError) as error:
                validate_database(value)
            self.assertEqual(error.exception.code, "incompatible_database")
        span = Span(0, 1, 1, 1, 1, 2)
        with self.assertRaises(BuildError) as error:
            encode(InlineInvocation("p", "reference", span, span))
        self.assertEqual(error.exception.code, "unsupported_node")

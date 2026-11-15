"""Expand invocations in order with isolated bindings and explicit call history."""

from dataclasses import fields

from sttv.common.errors import BuildError
from ..nodes import InlineInvocation, Located
from ..parser import parse_source
from ..traversal import sequences
from .binding import invocation
from .substitution import substitute


class Expansion:
    def __init__(self, templates, options, report=None):
        self.templates, self.options, self.report = templates, options, report
        self.records, self.stack, self.warnings = [], [], []
        self.counts = dict(encountered=0, expanded=0, failed=0, template_files=0, max_depth=0)

    def expand(self, document, syntax):
        self.records, self.stack = [], []
        self.root_source = document.source.origin(0, 0)
        try:
            self.sequence(document.items, document.source, syntax)
            containers = {id(items): path for path, items in sequences(document.items)}
            for record in self.records:
                record["insertion"] = {"container": containers[id(record.pop("_items"))],
                                       "index": record.pop("_index"), "count": record.pop("_count")}
            document.metadata["inline_scripts"].extend(self.records)
            return document
        finally:
            self.counts["template_files"] = len(self.templates.manifest)

    def sequence(self, items, source, syntax):
        result = []
        for node in items:
            if isinstance(node, InlineInvocation):
                first, index = len(self.records), len(result)
                expanded = expand_inline_script(node, source, syntax, self)
                record = self.records[first]
                record.update(_items=items, _index=index, _count=len(expanded))
                for child in self.records[first + 1:]:
                    if child["_items"] is expanded:
                        child["_items"] = items
                        child["_index"] += index
                result.extend(expanded)
            else:
                self.children(node, source, syntax)
                result.append(node)
        items[:] = result

    def children(self, node, source, syntax):
        for field in fields(node):
            value = getattr(node, field.name)
            if field.name == "items":
                self.sequence(value, source, syntax)
            elif isinstance(value, Located):
                self.children(value, source, syntax)

    def call(self, node, source, syntax):
        self.counts["encountered"] += 1
        record = {"id": f"inline_{self.counts['encountered']}",
                  "parent_id": self.stack[-1]["id"] if self.stack else None,
                  "call_site": node.origin, "form": node.form}
        self.records.append(record)
        frame = {"id": record["id"], "template": None, "call_site": node.origin}
        self.stack.append(frame)
        self.counts["max_depth"] = max(self.counts["max_depth"], len(self.stack))
        try:
            if len(self.stack) > self.options["max_depth"]:
                raise BuildError("inline_depth", "Inline expansion depth exceeded")
            path, raw, arguments, bindings = invocation(node, source, syntax, self.options)
            identity, relative, _ = self.templates.identity(path.text)
            record.update(script={"raw": raw, "value": path.text}, template=relative, arguments=arguments)
            frame.update(template=relative, identity=identity)
            if any(parent.get("identity") == identity for parent in self.stack[:-1]):
                raise BuildError("inline_cycle", f"Recursive template: {relative}")
            template = self.templates.read(path.text)
            expanded, used = substitute(template, bindings, syntax, self.options, record["id"])
            document = parse_source(expanded, syntax)
            self.sequence(document.items, expanded, syntax)
            unused = sorted(bindings.keys() - used)
            if unused:
                message = f"{relative}: unused arguments: {', '.join(unused)}"
                self.warnings.append({"code": "unused_inline_argument", "message": message, "call_id": record["id"]})
                if self.report is not None:
                    self.report.add("warning", "unused_inline_argument", "expansion", message,
                                    source=node.origin["root"], file=node.origin["file"],
                                    line=node.origin["span"]["line"])
            self.counts["expanded"] += 1
            return document.items
        except (BuildError, OSError, ValueError, RecursionError) as exc:
            self.counts["failed"] += 1
            if not isinstance(exc, BuildError):
                exc = BuildError("inline_expansion", str(exc))
            if not hasattr(exc, "call_chain"):
                exc.call_chain = [{k: v for k, v in entry.items() if k != "identity"} for entry in self.stack]
                exc.root_source = self.root_source
                exc.provenance = getattr(exc, "provenance", node.origin)
            raise exc
        finally:
            self.stack.pop()


def expand_inline_script(node, source, syntax, expansion):
    return expansion.call(node, source, syntax)

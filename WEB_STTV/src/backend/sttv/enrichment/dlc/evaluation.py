"""Small condition evaluation entry point, using the shared graph compiler."""

from .conditions import Compiler
from .graph import Graph, conjunction, disjunction, invert


class Evaluator:
    def __init__(self, names, enabled, rules):
        self.names, self.enabled, self.rules = names, enabled, rules
        self.diagnostics = []

    def evaluate(self, node, pointer, *, wrapper=False):
        graph = Graph(self.rules['limits'])
        compiler = Compiler(graph, self.names, self.rules)
        if wrapper:
            from .controls import compile_block
            root = compile_block(compiler, node, pointer, 'country', 0, self.rules['ignored_wrapper_fields'])
        else:
            root = compiler.compile(node, pointer)
        values = graph.evaluate(self.enabled)
        self.diagnostics.extend(graph.diagnostics)
        return graph.trace(root, values)

    def combine(self, trace, children, operator):
        fn = disjunction if operator in ('OR', 'NOR') else conjunction
        trace.update(operator=operator, children=children)
        for key in ('value', 'baseline'):
            result = fn([child[key] for child in children])
            trace[key] = invert(result) if operator in ('NOT', 'NAND', 'NOR') else result
        return trace

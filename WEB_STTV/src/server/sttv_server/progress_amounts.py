"""Read numeric research fractions and the workforce-based script value."""

import ast
from decimal import Decimal
import re

from .progress_sources import first, key, text
from .tree.ast import number


def constant(expression):
    expression = re.sub(r'\|([^|]+)\|', r'abs(\1)', expression).strip()
    operators = {ast.Add: Decimal.__add__, ast.Sub: Decimal.__sub__,
                 ast.Mult: Decimal.__mul__, ast.Div: Decimal.__truediv__}

    def value(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return Decimal(ast.get_source_segment(expression, node))
        if isinstance(node, ast.BinOp) and type(node.op) in operators:
            return operators[type(node.op)](value(node.left), value(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            return value(node.operand) * (-1 if isinstance(node.op, ast.USub) else 1)
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'abs'
                and len(node.args) == 1 and not node.keywords):
            return abs(value(node.args[0]))
        raise ValueError('Not a constant arithmetic expression')

    try:
        return value(ast.parse(expression, mode='eval').body)
    except (SyntaxError, ValueError, ArithmeticError):
        return None


def quantity(node):
    if node.get('kind') == 'scalar':
        result = number(node['text'])
    elif node.get('kind') == 'formula':
        result = constant(node['body'])
    else:
        result = None
    if result is not None:
        return {'percent': format((100 * result).normalize(), 'f')}
    body = node.get('body', {})
    if isinstance(body, dict) and [key(n) for n in body.get('items', [])] == ['base', 'mult', 'divide', 'max']:
        count = first(body, 'mult').get('body', {})
        trigger = first(count, 'complex_trigger_modifier')
        params = first(trigger, 'parameters')
        tags = first(params, 'tags').get('items', [])
        base, divisor, cap = (number(text(body, k)) for k in ('base', 'divide', 'max'))
        if (len(count.get('items', [])) == 1 and text(trigger, 'trigger') == 'total_country_workforce_with_job_tag'
                and text(trigger, 'mode') == 'add' and [t.get('text') for t in tags] == ['test_subject']
                and base is not None and divisor and cap is not None):
            return {'per_subject': format((base * 100 / divisor).normalize(), 'f'),
                    'maximum': format((cap * 100).normalize(), 'f')}
    return {'expression': node}

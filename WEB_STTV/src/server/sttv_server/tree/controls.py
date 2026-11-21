"""Trigger-only branching and bounded counts; no execution of game effects."""

from .ast import number


def compile_block(compiler, node, pointer, context, depth, ignored=()):
    children, items, i = [], node['items'], 0
    while i < len(items):
        item, path = items[i], f'{pointer}/items/{i}'
        key = item.get('key', {}).get('text')
        if key == 'if' and context != 'government':
            chain = [(item, path)]
            i += 1
            while i < len(items) and items[i].get('key', {}).get('text') in ('else_if', 'else'):
                chain.append((items[i], f'{pointer}/items/{i}'))
                i += 1
                if chain[-1][0]['key']['text'] == 'else':
                    break
            children.append(compile_branches(compiler, chain, context, depth + 1))
            continue
        if key not in ignored:
            children.append(compiler.compile(item, path, context, depth + 1))
        i += 1
    return compiler.graph.add('AND', children, pointer=pointer, context=context)


def compile_branches(compiler, chain, context, depth):
    tail = compiler.graph.add('constant', constant=True)
    for item, path in reversed(chain):
        body = item.get('value', {})
        if item.get('operator') != '=' or body.get('kind') != 'block':
            return compiler.unknown(item, path, context, 'unsupported_dlc_branch')
        key = item['key']['text']
        limits = [(i, n) for i, n in enumerate(body['items']) if n.get('key', {}).get('text') == 'limit']
        if key == 'else':
            if limits:
                return compiler.unknown(item, path, context, 'unsupported_dlc_branch')
            tail = compiler.compile(body, path + '/value', context, depth + 1)
            continue
        if len(limits) != 1:
            return compiler.unknown(item, path, context, 'unsupported_dlc_branch')
        index, limit = limits[0]
        guard = compiler.compile(limit['value'], f'{path}/value/items/{index}/value', context, depth + 1)
        yes = compile_block(compiler, body, path + '/value', context, depth + 1, ignored=('limit',))
        tail = compiler.graph.add('branch', [guard, yes, tail], pointer=path, context=context)
    return tail


def compile_count(compiler, node, pointer, context, depth):
    amounts = [n for n in node['items'] if n.get('key', {}).get('text') == 'amount']
    if len(amounts) != 1:
        return compiler.unknown(node, pointer, context, 'unsupported_dlc_count')
    amount = amounts[0]
    threshold = number(amount['value'].get('text'))
    if threshold is None or amount['operator'] not in ('=', '!=', '<', '<=', '>', '>='):
        return compiler.unknown(node, pointer, context, 'unsupported_dlc_count')
    children = [compiler.compile(n, f'{pointer}/items/{i}', context, depth + 1)
                for i, n in enumerate(node['items']) if n is not amount]
    return compiler.graph.add('count', children, threshold=str(threshold), comparison=amount['operator'],
                              pointer=pointer, context=context)

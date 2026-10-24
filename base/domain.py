"""
Odoo-style domain parser: converts a domain (list of triples, optionally
combined with logical prefix operators '&', '|', '!') into a Django Q object.

Domain examples:
    [('is_active', '=', True)]
    ['&', ('is_active', '=', True), ('module', '=', 3)]
    ['|', ('field_type', '=', 'VARCHAR'), ('field_type', '=', 'TEXT')]

Leaves with no explicit '&'/'|' between them are implicitly AND-ed together,
exactly like Odoo does.

Supported operators: =, !=, >, >=, <, <=, like, ilike, not ilike, in, not in
"""
from django.db.models import Q


def _leaf_to_q(field, op, value):
    if op == '=':
        return Q(**{field: value})
    if op == '!=':
        return ~Q(**{field: value})
    if op == '>':
        return Q(**{f'{field}__gt': value})
    if op == '>=':
        return Q(**{f'{field}__gte': value})
    if op == '<':
        return Q(**{f'{field}__lt': value})
    if op == '<=':
        return Q(**{f'{field}__lte': value})
    if op == 'like':
        return Q(**{f'{field}__contains': value})
    if op == 'ilike':
        return Q(**{f'{field}__icontains': value})
    if op == 'not ilike':
        return ~Q(**{f'{field}__icontains': value})
    if op == 'in':
        return Q(**{f'{field}__in': value})
    if op == 'not in':
        return ~Q(**{f'{field}__in': value})
    raise ValueError(f'Unsupported domain operator: {op}')


def domain_to_q(domain):
    """Evaluate an Odoo-style prefix-notation domain into a Django Q object."""
    if not domain:
        return Q()

    stack = []
    for token in reversed(domain):
        if token == '&':
            b, a = stack.pop(), stack.pop()
            stack.append(a & b)
        elif token == '|':
            b, a = stack.pop(), stack.pop()
            stack.append(a | b)
        elif token == '!':
            a = stack.pop()
            stack.append(~a)
        else:
            field, op, value = token
            stack.append(_leaf_to_q(field, op, value))

    # Any leaves left un-consumed by an explicit operator are implicitly AND-ed.
    while len(stack) > 1:
        b, a = stack.pop(), stack.pop()
        stack.append(a & b)

    return stack[0] if stack else Q()

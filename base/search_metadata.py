"""
Builds Odoo-like search panel metadata (filterable fields, groupable fields,
operator choices) DYNAMICALLY from IrModel / IrModelFields, and applies a
domain + group_by against the real Django queryset for that model.

Also provides get_widget_config(), the single place that decides which HTML
widget a field_type renders as -- used by any generic editable form (the
model/field metadata forms today, and any future generic "edit a record"
page) so the field_type -> widget mapping only has to be defined once.
"""
import json
from itertools import groupby
from operator import attrgetter

from django.apps import apps
from django.db.models import Q

from base.domain import domain_to_q
from base.auth_helpers import get_current_ir_user

# Operators offered in the "Add Custom Filter" builder per ir_model_fields.field_type.
# Mirrors the operator sets Odoo exposes per field type in its own filter builder.
OPERATORS_BY_TYPE = {
    'VARCHAR':  [['ilike', 'contains'], ['not ilike', 'does not contain'], ['=', 'is equal to']],
    'TEXT':     [['ilike', 'contains'], ['not ilike', 'does not contain']],
    'INTEGER':  [['=', '='], ['!=', '!='], ['>', '>'], ['>=', '>='], ['<', '<'], ['<=', '<=']],
    'DECIMAL':  [['=', '='], ['!=', '!='], ['>', '>'], ['>=', '>='], ['<', '<'], ['<=', '<=']],
    'BOOLEAN':  [['=', 'is']],
    'DATE':     [['=', 'is'], ['>', 'after'], ['<', 'before'], ['>=', 'on/after'], ['<=', 'on/before']],
    'DATETIME': [['=', 'is'], ['>', 'after'], ['<', 'before'], ['>=', 'on/after'], ['<=', 'on/before']],
    'FK':       [['=', 'is'], ['!=', 'is not']],
}

# Field types that make sensible "Group By" candidates -- same rationale Odoo
# uses (booleans, relations, and dates group naturally; free text doesn't).
GROUPABLE_TYPES = {'BOOLEAN', 'FK', 'DATE', 'DATETIME'}

# field_type -> widget _form_view.html should render when the field is editable.
# This is the single source of truth for that mapping -- extend here, not per-view.
WIDGET_BY_TYPE = {
    'BOOLEAN':  {'widget': 'checkbox'},
    'TEXT':     {'widget': 'textarea'},
    'INTEGER':  {'widget': 'number', 'step': '1'},
    'DECIMAL':  {'widget': 'number', 'step': 'any'},
    'DATE':     {'widget': 'date'},
    'DATETIME': {'widget': 'datetime'},
    'FK':       {'widget': 'many2one'},
    # VARCHAR and anything unrecognized falls back to plain text.
}


def get_widget_config(field_type):
    """Returns {'widget': ..., <extra attrs>} for a given ir_model_fields.field_type."""
    return WIDGET_BY_TYPE.get(field_type, {'widget': 'text'})


def _label(field_name):
    return field_name.replace('_', ' ').title()


def get_operators_json():
    return json.dumps(OPERATORS_BY_TYPE)


def get_relation_model_choices():
    """(id, model_name) pairs for every active IrModel -- used to populate the
    'Relation' dropdown when a field's type is FK."""
    from base.models import IrModel
    return [(m.id, m.model_name) for m in IrModel.objects.filter(is_active=True).order_by('model_name')]


def get_search_metadata(ir_model):
    """
    Returns (filterable_fields, groupable_fields) for a given IrModel row,
    built dynamically from its IrModelFields records -- filtered down to
    fields that actually exist as concrete columns on the real Django model.
    """
    from base.models import IrModelFields  # local import avoids circulars

    if not ir_model:
        return [], []

    django_model = get_django_model(ir_model)
    field_rows = IrModelFields.objects.filter(model=ir_model, is_active=True).order_by('field_name')

    filterable_fields = []
    groupable_fields = []

    for f in field_rows:
        if not is_concrete_field(django_model, f.field_name):
            continue
        entry = {
            'name': f.field_name,
            'label': _label(f.field_name),
            'field_type': f.field_type,
            'operators': OPERATORS_BY_TYPE.get(f.field_type, [['=', 'is']]),
        }
        filterable_fields.append(entry)
        if f.field_type in GROUPABLE_TYPES:
            groupable_fields.append(entry)

    return filterable_fields, groupable_fields


def get_django_model(ir_model):
    """Resolve the real Django model class behind an IrModel row."""
    if not ir_model:
        return None
    for model in apps.get_models():
        if getattr(model, '_name', None) == ir_model.model_name:
            return model
        if model._meta.db_table == ir_model.table_name:
            return model
    try:
        if '.' in ir_model.model_name:
            app_label, model_name = ir_model.model_name.split('.', 1)
            return apps.get_model(app_label, model_name)
    except Exception:
        pass
    return None



def is_concrete_field(django_model, field_name):
    """
    True only for real, queryable columns on the model -- excludes reverse
    relations (e.g. the 'irmodelfields' accessor IrModelFields.model creates
    back on IrModel) and anything else that isn't an actual field.

    ir_model_fields can end up with stale/bad rows (e.g. from an older
    version of sync_ir_models, or a manual edit), so filtering is done here
    rather than trusting the table -- this is what stops a bad row from ever
    reaching the search panel or crashing group-by again.
    """
    try:
        f = django_model._meta.get_field(field_name)
    except Exception:
        return False
    return getattr(f, 'concrete', False)


def apply_search(queryset, domain, search_query=None, search_fields=None):
    """Apply an Odoo-style domain (and optional free-text search) to a queryset."""
    if domain:
        queryset = queryset.filter(domain_to_q(domain))
    if search_query and search_fields:
        q = Q()
        for f in search_fields:
            q |= Q(**{f'{f}__icontains': search_query})
        queryset = queryset.filter(q)
    return queryset


def apply_group_by(dataset, group_by_field):
    """
    Groups an already-filtered queryset or list of records by a single field, Odoo-style.
    Supports concrete columns, properties, dictionary keys, and nested lookups (e.g. employee.department).
    Returns a list of {'key', 'label', 'count', 'rows'} dicts.
    """
    if not group_by_field or dataset is None:
        return None

    def resolve_val(obj, field_path):
        parts = field_path.replace('__', '.').split('.')
        curr = obj
        for p in parts:
            if curr is None:
                return None
            if isinstance(curr, dict):
                curr = curr.get(p)
            elif hasattr(curr, p):
                curr = getattr(curr, p)
            else:
                return None
        return curr

    from collections import OrderedDict
    buckets = OrderedDict()
    custom_labels = {}
    ordering_keys = []

    rows = dataset if isinstance(dataset, (list, tuple)) else list(dataset)

    # 1. Specialized pre-seeding for Leave Request status stages
    if group_by_field == 'status':
        ordering_keys = ['confirm', 'validate', 'refuse']
        custom_labels = {
            'confirm': 'To Approve',
            'validate': 'Approved',
            'refuse': 'Refused',
            'draft': 'Draft',
        }
        for k in ordering_keys:
            buckets[k] = []

    # 2. Specialized pre-seeding for Department (Employee model)
    elif group_by_field in ('department', 'department_rel'):
        try:
            from employee.models import Department
            depts = list(Department.objects.filter(is_active=True).order_by('name'))
            for d in depts:
                buckets[d.name] = []
                ordering_keys.append(d.name)
        except Exception:
            pass

    for row in rows:
        val = resolve_val(row, group_by_field)

        # Handle object values (e.g. Department or LeaveType foreign keys)
        if hasattr(val, 'name'):
            key = val.name
        elif hasattr(val, 'id') and not isinstance(val, (int, str)):
            key = str(val)
        else:
            key = val

        # Normalize status aliases
        if group_by_field == 'status':
            if key in ('Pending', 'To Approve'):
                key = 'confirm'
            elif key in ('Approved',):
                key = 'validate'
            elif key in ('Rejected', 'Refused'):
                key = 'refuse'

        if key in buckets:
            buckets[key].append(row)
        else:
            buckets[key] = [row]

    groups = []
    for key, items in buckets.items():
        if key in custom_labels:
            label = custom_labels[key]
        elif isinstance(key, bool):
            label = 'Yes' if key else 'No'
        elif hasattr(key, 'name'):
            label = str(key.name)
        elif key not in (None, ''):
            label = str(key)
        else:
            label = 'Unassigned'

        raw_val = getattr(key, 'id', key) if hasattr(key, 'id') else key
        groups.append({'key': key, 'raw_val': raw_val, 'label': label, 'count': len(items), 'rows': items})

    # Sort groups: if ordering_keys defined, follow that sequence; otherwise alphabetical
    if ordering_keys:
        order_map = {k: idx for idx, k in enumerate(ordering_keys)}
        groups.sort(key=lambda g: order_map.get(g['key'], 999))
    else:
        groups.sort(key=lambda g: str(g['label']))

    return groups


def get_favorites(request, model_key):
    """Returns saved filters (IrFilters) visible to the current user for a given model_key ('app_label.model_name')."""
    from base.models import IrFilters, IrModel

    ir_model = IrModel.objects.filter(model_name=model_key).first()
    if not ir_model:
        return []

    current_user = get_current_ir_user(request)
    qs = IrFilters.objects.filter(model=ir_model, is_active=True)
    qs = qs.filter(Q(user=current_user) | Q(user__isnull=True)) if current_user else qs.filter(user__isnull=True)

    favorites = list(qs.order_by('sequence', 'name'))
    for fav in favorites:
        fav.domain_json = json.dumps(fav.domain)
    return favorites

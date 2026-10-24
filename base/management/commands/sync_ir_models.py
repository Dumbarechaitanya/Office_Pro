from django.core.management.base import BaseCommand
from django.apps import apps
from base.models import IrModel, IrModelFields, IrModule


FIELD_TYPE_MAP = {
    'CharField': 'VARCHAR',
    'TextField': 'TEXT',
    'IntegerField': 'INTEGER',
    'BigIntegerField': 'INTEGER',
    'SmallIntegerField': 'INTEGER',
    'PositiveIntegerField': 'INTEGER',
    'BigAutoField': 'INTEGER',
    'AutoField': 'INTEGER',
    'DecimalField': 'DECIMAL',
    'FloatField': 'DECIMAL',
    'BooleanField': 'BOOLEAN',
    'DateField': 'DATE',
    'DateTimeField': 'DATETIME',
    'TimeField': 'DATETIME',
    'ForeignKey': 'FK',
    'OneToOneField': 'FK',
    'ManyToManyField': 'FK',
    'EmailField': 'VARCHAR',
    'URLField': 'VARCHAR',
    'UUIDField': 'VARCHAR',
    'SlugField': 'VARCHAR',
    'JSONField': 'TEXT',
}


class Command(BaseCommand):
    help = 'Automatically discover and sync all Django models/fields across all installed apps into ir_model and ir_model_fields'

    def handle(self, *args, **options):
        synced_models = 0
        synced_fields = 0
        active_model_ids = []

        for model in apps.get_models():
            app_label = model._meta.app_label

            # Skip Django internal core apps
            if app_label in ('admin', 'auth', 'contenttypes', 'sessions'):
                continue

            # Model technical identifier (e.g. hr.leave or base.rescompany)
            model_name = getattr(model, '_name', f"{app_label}.{model._meta.model_name}")
            table_name = model._meta.db_table
            module_name = getattr(model, '_module', model_name.split('.')[0] if '.' in model_name else app_label)

            module_obj, _ = IrModule.objects.get_or_create(
                name=module_name,
                defaults={'state': 'installed'}
            )

            description = getattr(model, '_description', str(model._meta.verbose_name).title())

            ir_model_obj, created = IrModel.objects.update_or_create(
                model_name=model_name,
                defaults={
                    'table_name': table_name,
                    'module': module_obj,
                    'description': description,
                    'is_active': True,
                }
            )
            active_model_ids.append(ir_model_obj.id)
            synced_models += 1

            for field in model._meta.get_fields():
                if not hasattr(field, 'get_internal_type'):
                    continue

                internal_type = field.get_internal_type()
                mapped_type = FIELD_TYPE_MAP.get(internal_type, 'VARCHAR')
                is_required = not getattr(field, 'blank', True)
                field_label = getattr(field, 'verbose_name', field.name)
                if hasattr(field_label, 'title'):
                    field_label = field_label.title()

                IrModelFields.objects.update_or_create(
                    model=ir_model_obj,
                    field_name=field.name,
                    defaults={
                        'field_type': mapped_type,
                        'is_required': is_required,
                    }
                )
                synced_fields += 1

        # Safely deactivate models whose tables no longer exist in any installed app
        if active_model_ids:
            IrModel.objects.exclude(id__in=active_model_ids).update(is_active=False)

        self.stdout.write(self.style.SUCCESS(
            f'Successfully synced {synced_models} models and {synced_fields} fields across all apps.'
        ))


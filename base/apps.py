from django.apps import AppConfig


class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'

    def ready(self):
        import django.db.models.signals as signals
        from django.core.management import call_command

        def run_sync(sender, **kwargs):
            try:
                call_command('sync_ir_models')
            except Exception:
                pass  # avoid crashing migrate if DB isn't ready yet

        signals.post_migrate.connect(run_sync)
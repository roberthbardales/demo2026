from django.apps import AppConfig


class InventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'applications.inventario'
    verbose_name = 'Inventario'

    def ready(self):
        import applications.inventario.signals  # noqa

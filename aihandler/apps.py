from django.apps import AppConfig
from django.db.models.signals import post_migrate

class AihandlerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "aihandler"
    
    def ready(self):
        """Ensure signals are imported only after migrations are complete."""
        post_migrate.connect(self.load_signals, sender=self)

    def load_signals(self, **kwargs):
        """Import signals only after all migrations are applied."""
        import aihandler.signals
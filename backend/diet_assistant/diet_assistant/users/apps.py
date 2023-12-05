from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "diet_assistant.users"
    verbose_name = "Users"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """
        Override this to put in:
        - Users system checks
        - Users signal registration
        """

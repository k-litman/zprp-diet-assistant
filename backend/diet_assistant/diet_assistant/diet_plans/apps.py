from django.apps import AppConfig


class DietPlansConfig(AppConfig):
    name = "diet_assistant.diet_plans"
    verbose_name = "Diet Plans"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """
        Override this to put in:
        - Users system checks
        - Users signal registration
        """

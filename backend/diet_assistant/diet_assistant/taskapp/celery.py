# Celery
from django.apps import AppConfig, apps

from celery import Celery

app = Celery("diet_assistant")


class CeleryConfig(AppConfig):
    name = "diet_assistant.taskapp"
    verbose_name = "Celery Config"

    def ready(self):
        # Using a string here means the worker will not have to
        # pickle the object when using Windows.
        app.config_from_object("django.conf:settings", namespace="CELERY")
        installed_apps = [app_config.name for app_config in apps.get_app_configs()]
        app.autodiscover_tasks(lambda: installed_apps, force=True)


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request}")  # pragma: no cover

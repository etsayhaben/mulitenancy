from django.apps import AppConfig


class TenantDbConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tenant_db"  # Must match your app folder name

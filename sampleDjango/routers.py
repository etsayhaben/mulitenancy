from django.conf import settings
from django_tenants.routers import TenantSyncRouter

class CustomTenantSyncRouter(TenantSyncRouter):
    def db_for_read(self, model, **hints):
        if model._meta.app_label in settings.SHARED_APPS:
            return "default"
        return "tenant_db"

    def db_for_write(self, model, **hints):
        if model._meta.app_label in settings.SHARED_APPS:
            return "default"
        return "tenant_db"

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == "default":
            return app_label in settings.SHARED_APPS
        elif db == "tenant_db":
            return app_label in settings.TENANT_APPS
        return None
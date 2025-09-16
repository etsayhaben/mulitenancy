# sampleDjango/routers.py
from django.conf import settings
from django_tenants.routers import TenantSyncRouter

class CustomTenantSyncRouter(TenantSyncRouter):
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == "default":
            return app_label in settings.SHARED_APPS
        elif db == "tenant_db":
            return app_label in settings.TENANT_APPS
        return None

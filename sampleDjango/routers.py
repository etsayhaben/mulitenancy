# sampleDjango/routers.py

from django.conf import settings
from django_tenants.routers import TenantSyncRouter as BaseTenantSyncRouter

class CustomTenantSyncRouter(BaseTenantSyncRouter):
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Allow migrations ONLY for SHARED_APPS in 'default' DB
        if db == "default":
            return app_label in settings.SHARED_APPS

        # Allow migrations ONLY for TENANT_APPS in 'tenant_db'
        if db == "tenant_db":
            return app_label in settings.TENANT_APPS

        # Disallow migrations for any other DB
        return False
# routers.py
class TenantRouter:
    """
    Routes models to the correct tenant database dynamically.
    """

    def db_for_read(self, model, **hints):
        tenant = hints.get("tenant")
        if tenant:
            return tenant.tenant_identifier
        return "default"  # fallback to master DB

    def db_for_write(self, model, **hints):
        tenant = hints.get("tenant")
        if tenant:
            return tenant.tenant_identifier
        return "default"

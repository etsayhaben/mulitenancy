from django.db import connections
from django_tenants.middleware.main import TenantMainMiddleware

class CustomTenantMiddleware(TenantMainMiddleware):
    def process_request(self, request):
        super().process_request(request)
        tenant = getattr(request, 'tenant', None)
        if tenant is None:
            connections['default'].schema_name = 'public'
            connections['tenant_db'].schema_name = 'public'
        else:
            connections['tenant_db'].schema_name = tenant.schema_name
            connections['default'].schema_name = 'public'
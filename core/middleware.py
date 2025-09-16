# core/middleware.py

from django.db import connection
from django.utils.deprecation import MiddlewareMixin
from master_db.models import Client  # Your tenant model in master_db

class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Example: Get tenant from subdomain
        host = request.get_host().split(':')[0]  # Remove port
        subdomain = host.split('.')[0]

        if subdomain == 'www' or subdomain == 'localhost':
            # Use default/master DB
            return

        try:
            tenant = Client.objects.get(sub_domain=subdomain)
            # Switch database connection to tenant's DB
            connection.close()  # Close current connection
            connection.settings_dict.update({
                'NAME': tenant.db_name,
                'USER': tenant.db_user,
                'PASSWORD': tenant.db_password,
                'HOST': tenant.db_host or 'localhost',
                'PORT': tenant.db_port or '5432',
            })
            # Reconnect on next query
        except Client.DoesNotExist:
            # Handle invalid tenant
            pass  # or raise 404
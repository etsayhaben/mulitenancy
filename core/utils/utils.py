# utils.py
from django.conf import settings
from django.db import connections

def get_tenant_connection(tenant):
    """
    Adds tenant DB settings dynamically and returns a connection.
    """
    settings.DATABASES[tenant.tenant_identifier] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': tenant.db_name,
        'USER': tenant.db_user,
        'PASSWORD': tenant.db_password,
        'HOST': 'localhost',
        'PORT': '5432',
    }
    return connections[tenant.tenant_identifier]

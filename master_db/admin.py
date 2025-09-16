# master_db/admin.py

from django.contrib import admin
from .models import Client, Domain
from .services import create_tenant

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'schema_name', 'created_on']
    actions = ['create_sample_tenant']

    def create_sample_tenant(self, request, queryset):
        # Not for queryset — just an example button
        tenant = create_tenant(
            name="Sample Company",
            domain="sample.localhost",
            contact_email="admin@sample.com",
            plan="pro",
        )
        self.message_user(request, f"Tenant {tenant.name} created with schema {tenant.schema_name}")
    create_sample_tenant.short_description = "Create sample tenant"
# master_db/services.py

from django.db import transaction
from django_tenants.utils import tenant_context
from .models import Client, Domain
from tenant_db.models import Product, CompanySettings # Import tenant-specific models

def create_tenant(name, domain, contact_email=None, plan='free'):
    """
    Create a new tenant with its schema and seed initial data.
    """
    # Wrap in transaction so if anything fails, nothing is created
    with transaction.atomic():
        # 1. Create Client → triggers schema creation in tenant_db
        tenant = Client.objects.create(
            name=name,
            schema_name=domain.split('.')[0],  # e.g., 'companya' from 'companya.localhost'
            contact_email=contact_email,
            plan=plan,
        )

        # 2. Create Domain
        Domain.objects.create(
            domain=domain,
            tenant=tenant,
            is_primary=True,
        )

        # 3. Seed initial data into the new tenant's schema
        with tenant_context(tenant):
            # Create default products
            Product.objects.bulk_create([
                Product(name="Default Product 1", price="9.99", stock=100),
                Product(name="Default Product 2", price="19.99", stock=50),
            ])

            # Create company settings
            CompanySettings.objects.create(
                company_name=name,
                currency="USD",
                timezone="UTC",
            )

            # Create any other initial data (categories, permissions, etc.)

        return tenant
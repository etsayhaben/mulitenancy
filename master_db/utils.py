import psycopg2
from django.conf import settings
from django.core.management import call_command


def create_tenant_database(tenant):
    """Create physical tenant database."""
    conn = psycopg2.connect(
        dbname="postgres",  # connect to default DB
        user=settings.DATABASES["default"]["USER"],
        password=settings.DATABASES["default"]["PASSWORD"],
        host=settings.DATABASES["default"]["HOST"],
        port=settings.DATABASES["default"]["PORT"],
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE {tenant.db_name};")
    cur.close()
    conn.close()


def add_tenant_to_settings(tenant):
    """Add tenant DB dynamically to settings."""
    """Add tenant DB dynamically to settings."""
    default_db = settings.DATABASES["default"]
    if tenant.db_name not in settings.DATABASES:
        settings.DATABASES[tenant.db_name] = {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": tenant.db_name,
            "USER": tenant.db_user,
            "PASSWORD": tenant.db_password,
            "HOST": settings.DATABASES["default"]["HOST"],
            "PORT": settings.DATABASES["default"]["PORT"],
            "OPTIONS": {"sslmode": "require"},  # ensure SSL
            "TIME_ZONE": default_db.get("TIME_ZONE", "UTC"),
            "ATOMIC_REQUESTS": False,
            "AUTOCOMMIT": default_db.get("AUTOCOMMIT", True),
            "CONN_HEALTH_CHECKS": default_db.get(
                "CONN_HEALTH_CHECKS", True
            ),  # <--- new
            "CONN_MAX_AGE": default_db.get("CONN_MAX_AGE", 0),  # <--- added
        }


def migrate_tenant(tenant):
    """Run migrations for tenant DB."""
    call_command("migrate", "tenant_db", database=tenant.db_name)


def create_tenant_superuser(tenant):
    """Create superuser for tenant DB."""
    from tenant_db.models import User

    User.objects.using(tenant.db_name).create_superuser(
        username="admin", email=f"admin@{tenant.db_name}.com", password="admin123"
    )

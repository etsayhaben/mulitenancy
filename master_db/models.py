from django.db import models, connections
from django_tenants.models import TenantMixin, DomainMixin
from django_tenants.migration_executors import get_executor
from django.contrib.auth.models import AbstractUser, BaseUserManager
from core.roles import RoleChoices, ROLE_TO_GROUP

class Client(TenantMixin):
    name = models.CharField(max_length=100, unique=True)
    created_on = models.DateField(auto_now_add=True)
    plan = models.CharField(max_length=20, default='free')  # e.g., 'free', 'pro', 'enterprise'
    contact_email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    auto_create_schema = True
    auto_drop_schema = False  # Never auto-drop in prod!

    def create_schema(self, check_if_exists=False, verbosity=1):
        """Override to create schema in tenant_db instead of default."""
        connection = connections['tenant_db']
        executor = get_executor()(connection, self)
        executor.create_schema(check_if_exists, verbosity)

    def delete_schema(self, check_if_exists=False, verbosity=1):
        """Override to delete schema from tenant_db."""
        connection = connections['tenant_db']
        executor = get_executor()(connection, self)
        executor.delete_schema(check_if_exists, verbosity)

    def __str__(self):
        return self.name

class Domain(DomainMixin):
    pass

class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", RoleChoices.CLERK.value)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", RoleChoices.SUPERADMIN.value)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.as_choices(),
        blank=False,
        null=False,
    )

    objects = UserManager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._assign_role_group()

    def _assign_role_group(self):
        from django.contrib.auth.models import Group
        group_name = ROLE_TO_GROUP.get(self.role)
        if not group_name:
            return
        group, created = Group.objects.get_or_create(name=group_name)
        self.groups.clear()
        self.groups.add(group)
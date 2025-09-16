# master_db/models.py

from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from core.roles import RoleChoices, ROLE_TO_GROUP
import uuid
from django_tenants.models import TenantMixin, DomainMixin
from django.contrib.auth.models import AbstractUser, BaseUserManager
# master_db/models.py

from django_tenants.models import TenantMixin, DomainMixin

class Client(TenantMixin):
    name = models.CharField(max_length=100, unique=True)
    created_on = models.DateField(auto_now_add=True)
    # Optional fields for your business logic
    plan = models.CharField(max_length=20, default='free')  # e.g., 'free', 'pro', 'enterprise'
    contact_email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # django-tenants will auto-create schema in TENANT_DATABASE_ALIAS
    auto_create_schema = True
    auto_drop_schema = False  # Never auto-drop in prod!

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
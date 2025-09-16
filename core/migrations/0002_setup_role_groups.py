# core/migrations/0002_setup_role_groups.py
"""
Set up Django Groups and Permissions for role-based access control.
"""

from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


CUSTOM_PERMISSIONS = [
    {
        "codename": "can_view_financial_reports",
        "name": "Can view financial reports",
        "app_label": "core",
    },
    {
        "codename": "can_process_payments",
        "name": "Can process payments",
        "app_label": "core",
    },
    {
        "codename": "can_manage_users",
        "name": "Can manage users",
        "app_label": "core",
    },
]

GROUP_PERMISSIONS = {
    "Super Admin": [
        "can_view_financial_reports",
        "can_process_payments",
        "can_manage_users",
    ],
    "Admin": ["can_view_financial_reports", "can_process_payments"],
    "Accountant": ["can_view_financial_reports"],
    "Clerk": [],
}


def create_groups_and_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")
    User = apps.get_model("core", "User")

    # ✅ Correct way: Get or create content type using only app_label and model
    content_type, created = ContentType.objects.get_or_create(
        app_label="core", model="user"
    )

    # Create permissions
    permission_objects = {}
    for perm in CUSTOM_PERMISSIONS:
        perm_obj, created = Permission.objects.get_or_create(
            codename=perm["codename"],
            content_type=content_type,
            defaults={"name": perm["name"]},
        )
        permission_objects[perm["codename"]] = perm_obj

    # Create groups and assign permissions
    for group_name, perm_codenames in GROUP_PERMISSIONS.items():
        group, created = Group.objects.get_or_create(name=group_name)
        perms_to_assign = [
            permission_objects[codename]
            for codename in perm_codenames
            if codename in permission_objects
        ]
        group.permissions.set(perms_to_assign)
        print(f"✅ Group '{group_name}' {'created' if created else 'updated'}")


def remove_groups_and_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for group_name in GROUP_PERMISSIONS:
        Group.objects.filter(name=group_name).delete()
        print(f"🗑️ Deleted group: {group_name}")


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            create_groups_and_permissions, reverse_code=remove_groups_and_permissions
        ),
    ]

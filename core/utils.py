# core/utils.py
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def setup_roles_and_permissions():
    """
    Creates default groups and permissions on first run.
    Safe to call multiple times (idempotent).
    Does NOT delete or modify existing groups/permissions.
    """
    from tenant_db.models import User
    from .roles import CUSTOM_PERMISSIONS

    # Step 1: Get or create content type for custom permissions
    try:
        content_type = ContentType.objects.get(app_label="core", model="user")
    except ContentType.DoesNotExist:
        content_type = ContentType.objects.create(
            app_label="core", model="user", name="User"
        )

    # Step 2: Create custom permissions (if they don't exist)
    # This ensures base permissions exist for role assignment
    for perm in CUSTOM_PERMISSIONS:
        Permission.objects.get_or_create(
            codename=perm["codename"],
            content_type=content_type,
            defaults={"name": perm["name"]},
        )

    # Step 3: Create default groups and assign base permissions
    # Only if they don't exist (safe for production)
    from .roles import GROUP_PERMISSIONS  # Import here to avoid circular import

    for group_name, perm_codenames in GROUP_PERMISSIONS.items():
        group, created = Group.objects.get_or_create(name=group_name)

        # Only assign permissions if group was just created
        # This prevents overwriting admin changes
        if created:
            permission_objects = []
            for codename in perm_codenames:
                try:
                    perm_obj = Permission.objects.get(
                        codename=codename, content_type=content_type
                    )
                    permission_objects.append(perm_obj)
                except Permission.DoesNotExist:
                    continue  # Skip invalid perms

            group.permissions.set(permission_objects)
            print(
                f"✅ Created group '{group_name}' with {len(permission_objects)} permission(s)"
            )
        else:
            print(
                f"🔁 Group '{group_name}' already exists. Skipping permission assignment to allow admin customization."
            )

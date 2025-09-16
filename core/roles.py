# core/roles.py
from enum import Enum


class RoleChoices(Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    CLERK = "clerk"

    @classmethod
    def as_choices(cls):
        return [(role.value, role.value.title()) for role in cls]


# 🔗 Role → Group Name (Single Source of Truth)
GROUP_NAMES = {
    RoleChoices.SUPERADMIN.value: "Super Admins",
    RoleChoices.ADMIN.value: "Admins",
    RoleChoices.ACCOUNTANT.value: "Accountants",
    RoleChoices.CLERK.value: "Clerks",
}

# Reverse: Group name → Role
ROLE_FROM_GROUP = {v: k for k, v in GROUP_NAMES.items()}
ROLE_TO_GROUP = {
    RoleChoices.SUPERADMIN.value: "Super Admin",
    RoleChoices.ADMIN.value: "Admin",
    RoleChoices.ACCOUNTANT.value: "Accountant",
    RoleChoices.CLERK.value: "Clerk",
}

# 🛠️ Custom Permissions (Domain Actions)
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
    {
        "codename": "can_approve_bill",
        "name": "Can approve bills",
        "app_label": "core",
    },
]

# 🎯 Group → Permissions Mapping (Your Security Policy)
GROUP_PERMISSIONS = {
    GROUP_NAMES["superadmin"]: [
        "can_view_financial_reports",
        "can_process_payments",
        "can_manage_users",
    ],
    GROUP_NAMES["admin"]: [
        "can_view_financial_reports",
        "can_process_payments",
    ],
    GROUP_NAMES["accountant"]: [
        "can_view_financial_reports",
    ],
    GROUP_NAMES["clerk"]: [],
}

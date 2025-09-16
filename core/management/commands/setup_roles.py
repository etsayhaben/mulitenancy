# core/management/commands/setup_roles.py
from django.core.management.base import BaseCommand
from core.utils import setup_roles_and_permissions


class Command(BaseCommand):
    help = "Set up role-based groups and permissions"

    def handle(self, *args, **options):
        setup_roles_and_permissions()
        self.stdout.write("✅ Roles and permissions set up.")
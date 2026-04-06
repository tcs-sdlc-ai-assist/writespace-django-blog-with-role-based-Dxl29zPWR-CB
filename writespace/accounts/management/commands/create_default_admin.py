import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates a default admin superuser if one does not already exist.'

    def handle(self, *args, **options):
        username = os.environ.get('DEFAULT_ADMIN_USERNAME', 'admin')
        password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'admin')
        email = os.environ.get('DEFAULT_ADMIN_EMAIL', 'admin@example.com')

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f'Admin user "{username}" already exists. Skipping creation.'
                )
            )
            return

        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Default admin user "{username}" created successfully.'
                )
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    f'Failed to create default admin user: {e}'
                )
            )
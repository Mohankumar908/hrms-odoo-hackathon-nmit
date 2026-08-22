"""
Management command to seed default Admin and HR accounts.
Usage: python manage.py seed_defaults
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.employees.models import EmployeeProfile, Department


class Command(BaseCommand):
    help = 'Creates default Admin and HR accounts if they do not exist.'

    DEFAULTS = [
        {
            'employee_id': 'ADMIN001',
            'email':       'admin@dayflow.com',
            'password':    'Admin@1234',
            'role':        'admin',
            'full_name':   'System Admin',
        },
        {
            'employee_id': 'HR001',
            'email':       'hr@dayflow.com',
            'password':    'Hr@12345',
            'role':        'hr',
            'full_name':   'HR Manager',
        },
    ]

    def handle(self, *args, **kwargs):
        created_any = False
        for d in self.DEFAULTS:
            if not User.objects.filter(email=d['email']).exists():
                user = User.objects.create_user(
                    email=d['email'],
                    employee_id=d['employee_id'],
                    password=d['password'],
                    role=d['role'],
                    is_email_verified=True,
                    is_staff=(d['role'] == 'admin'),
                    is_superuser=(d['role'] == 'admin'),
                )
                from apps.employees.models import EmployeeProfile
                EmployeeProfile.objects.get_or_create(
                    user=user,
                    defaults={'full_name': d['full_name'], 'first_name': d['full_name'].split()[0], 'employment_status': 'active'}
                )
                self.stdout.write(self.style.SUCCESS(
                    f"Created {d['role'].upper()}: {d['email']}  password: {d['password']}"
                ))
                created_any = True
            else:
                self.stdout.write(self.style.WARNING(
                    f"Already exists: {d['email']} — skipped"
                ))

        if not created_any:
            self.stdout.write('All default accounts already exist.')

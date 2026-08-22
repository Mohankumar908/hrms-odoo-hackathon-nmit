"""
Management command: seed 10 predefined leave types.
Usage: python manage.py seed_leave_types
"""
from django.core.management.base import BaseCommand
from apps.leave_management.models import LeaveType

LEAVE_TYPES = [
    {'name': 'Casual Leave',       'description': 'For personal/casual matters.',          'max_days_per_year': 12,  'is_paid': True},
    {'name': 'Sick Leave',         'description': 'For illness or medical appointments.',   'max_days_per_year': 15,  'is_paid': True},
    {'name': 'Earned Leave',       'description': 'Leave earned through service.',          'max_days_per_year': 18,  'is_paid': True},
    {'name': 'Annual Leave',       'description': 'Yearly paid vacation leave.',            'max_days_per_year': 21,  'is_paid': True},
    {'name': 'Maternity Leave',    'description': 'For female employees before/after childbirth.', 'max_days_per_year': 90, 'is_paid': True},
    {'name': 'Paternity Leave',    'description': 'For male employees on birth of child.',  'max_days_per_year': 7,   'is_paid': True},
    {'name': 'Bereavement Leave',  'description': 'For death of an immediate family member.','max_days_per_year': 5,  'is_paid': True},
    {'name': 'Marriage Leave',     'description': 'For own marriage.',                      'max_days_per_year': 5,   'is_paid': True},
    {'name': 'Compensatory Leave', 'description': 'For working on holidays/weekends.',      'max_days_per_year': 0,   'is_paid': True},
    {'name': 'Unpaid Leave',       'description': 'Leave without pay approval.',            'max_days_per_year': 0,   'is_paid': False},
]


class Command(BaseCommand):
    help = 'Seeds 10 predefined leave types.'

    def handle(self, *args, **kwargs):
        created = 0
        for lt in LEAVE_TYPES:
            obj, new = LeaveType.objects.get_or_create(
                name=lt['name'],
                defaults={
                    'description':       lt['description'],
                    'max_days_per_year': lt['max_days_per_year'],
                    'is_paid':           lt['is_paid'],
                    'requires_approval': True,
                    'is_active':         True,
                }
            )
            if new:
                self.stdout.write(self.style.SUCCESS(f'  Created: {obj.name}'))
                created += 1
            else:
                self.stdout.write(self.style.WARNING(f'  Exists:  {obj.name}'))
        self.stdout.write(self.style.SUCCESS(f'\n{created} leave types created.'))

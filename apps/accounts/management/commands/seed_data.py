"""
DAYFLOW HRMS - Seed initial data.
Run: python manage.py seed_data
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed DAYFLOW with initial leave types, departments, and demo users.'

    def handle(self, *args, **kwargs):
        from apps.leave_management.models import LeaveType
        from apps.employees.models import Department, Designation

        # Leave types
        leave_types = [
            {'name': 'Paid Leave', 'max_days_per_year': 15, 'is_paid': True},
            {'name': 'Sick Leave', 'max_days_per_year': 10, 'is_paid': True},
            {'name': 'Unpaid Leave', 'max_days_per_year': 0, 'is_paid': False},
            {'name': 'Casual Leave', 'max_days_per_year': 7, 'is_paid': True},
            {'name': 'Maternity Leave', 'max_days_per_year': 90, 'is_paid': True},
        ]
        for lt in leave_types:
            obj, created = LeaveType.objects.get_or_create(name=lt['name'], defaults=lt)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created leave type: {lt["name"]}'))

        # Departments
        departments = ['Engineering', 'Human Resources', 'Finance', 'Marketing', 'Operations', 'Design', 'Sales']
        dept_objs = {}
        for d in departments:
            obj, created = Department.objects.get_or_create(name=d)
            dept_objs[d] = obj
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created department: {d}'))

        # Designations
        designations = {
            'Engineering': ['Software Engineer', 'Senior Engineer', 'Tech Lead', 'DevOps Engineer'],
            'Human Resources': ['HR Executive', 'HR Manager', 'Recruiter'],
            'Finance': ['Accountant', 'Finance Manager', 'Analyst'],
            'Marketing': ['Marketing Executive', 'Content Writer', 'SEO Specialist'],
            'Operations': ['Operations Manager', 'Coordinator'],
            'Design': ['UI/UX Designer', 'Graphic Designer'],
            'Sales': ['Sales Executive', 'Sales Manager'],
        }
        for dept_name, titles in designations.items():
            dept = dept_objs.get(dept_name)
            if dept:
                for title in titles:
                    obj, created = Designation.objects.get_or_create(title=title, department=dept)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created designation: {title}'))

        self.stdout.write(self.style.SUCCESS('Seed complete!'))

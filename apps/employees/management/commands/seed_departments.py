"""
Management command: seed default departments and designations.
Usage: python manage.py seed_departments
"""
from django.core.management.base import BaseCommand
from apps.employees.models import Department, Designation

DATA = [
    {
        'name': 'Human Resources',
        'description': 'Manages recruitment, employee relations, and HR operations.',
        'designations': [
            'HR Manager', 'HR Executive', 'HR Assistant', 'Recruiter', 'Payroll Officer',
        ],
    },
    {
        'name': 'Engineering',
        'description': 'Software development and technical operations.',
        'designations': [
            'Software Engineer', 'Senior Software Engineer', 'Tech Lead',
            'DevOps Engineer', 'QA Engineer', 'Engineering Manager',
        ],
    },
    {
        'name': 'Product',
        'description': 'Product management and design.',
        'designations': [
            'Product Manager', 'Associate Product Manager', 'UI/UX Designer',
            'Product Analyst', 'Product Director',
        ],
    },
    {
        'name': 'Finance',
        'description': 'Financial planning, accounting, and reporting.',
        'designations': [
            'Finance Manager', 'Accountant', 'Financial Analyst',
            'Accounts Executive', 'Chief Financial Officer',
        ],
    },
    {
        'name': 'Sales',
        'description': 'Sales and business development.',
        'designations': [
            'Sales Executive', 'Sales Manager', 'Business Development Manager',
            'Account Manager', 'VP of Sales',
        ],
    },
    {
        'name': 'Marketing',
        'description': 'Brand, digital, and growth marketing.',
        'designations': [
            'Marketing Executive', 'Marketing Manager', 'Content Writer',
            'SEO Specialist', 'Brand Manager',
        ],
    },
    {
        'name': 'Operations',
        'description': 'Business operations and process management.',
        'designations': [
            'Operations Manager', 'Operations Executive', 'Process Analyst',
            'Logistics Coordinator', 'COO',
        ],
    },
    {
        'name': 'Customer Support',
        'description': 'Customer service and support.',
        'designations': [
            'Support Executive', 'Support Lead', 'Customer Success Manager',
            'Technical Support Specialist',
        ],
    },
    {
        'name': 'Administration',
        'description': 'General administration and office management.',
        'designations': [
            'Admin Executive', 'Office Manager', 'Receptionist',
            'Administrative Assistant',
        ],
    },
    {
        'name': 'Legal',
        'description': 'Legal compliance and corporate affairs.',
        'designations': [
            'Legal Counsel', 'Compliance Officer', 'Legal Executive',
        ],
    },
]


class Command(BaseCommand):
    help = 'Seeds default departments and designations.'

    def handle(self, *args, **kwargs):
        dept_created = 0
        desig_created = 0

        for item in DATA:
            dept, d_new = Department.objects.get_or_create(
                name=item['name'],
                defaults={'description': item['description']}
            )
            if d_new:
                self.stdout.write(self.style.SUCCESS(f'  Dept created : {dept.name}'))
                dept_created += 1
            else:
                self.stdout.write(f'  Dept exists  : {dept.name}')

            for title in item['designations']:
                des, des_new = Designation.objects.get_or_create(
                    title=title, department=dept,
                    defaults={'description': ''}
                )
                if des_new:
                    self.stdout.write(self.style.SUCCESS(f'    + {des.title}'))
                    desig_created += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n{dept_created} departments and {desig_created} designations created.'
        ))

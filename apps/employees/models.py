"""
DAYFLOW HRMS - Employee profiles, departments, designations, documents.
"""
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class Department(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='headed_department'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Designation(TimeStampedModel):
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='designations')
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ['title', 'department']
        ordering = ['title']

    def __str__(self):
        return f'{self.title} - {self.department.name}'


class EmployeeProfile(TimeStampedModel):
    GENDER_CHOICES = [
        ('male', 'Male'), ('female', 'Female'),
        ('other', 'Other'), ('prefer_not', 'Prefer not to say'),
    ]
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
        ('probation', 'Probation'),
    ]
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile'
    )
    first_name = models.CharField(max_length=80, blank=True)
    last_name  = models.CharField(max_length=80, blank=True)
    full_name  = models.CharField(max_length=150)   # kept for backwards compat
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=15, choices=GENDER_CHOICES, blank=True)
    phone  = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    # Job details
    department   = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name='employees')
    designation  = models.ForeignKey(Designation, null=True, blank=True, on_delete=models.SET_NULL, related_name='employees')
    joining_date = models.DateField(null=True, blank=True)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default='active')
    employment_type   = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='subordinates'
    )

    class Meta:
        db_table = 'employees_profile'
        verbose_name = 'Employee Profile'

    def __str__(self):
        return f'{self.full_name} ({self.user.employee_id})'

    def save(self, *args, **kwargs):
        # Auto-sync full_name from first+last if provided
        if self.first_name or self.last_name:
            self.full_name = f'{self.first_name} {self.last_name}'.strip()
        super().save(*args, **kwargs)

    @property
    def profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/images/default_avatar.png'


class SalaryStructure(TimeStampedModel):
    employee = models.OneToOneField(EmployeeProfile, on_delete=models.CASCADE, related_name='salary_structure')
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    house_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    provident_fund = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    effective_from = models.DateField()
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'employees_salary_structure'

    def __str__(self):
        return f'Salary: {self.employee.full_name}'

    @property
    def total_allowances(self):
        return (self.house_allowance + self.transport_allowance +
                self.medical_allowance + self.other_allowances)

    @property
    def total_deductions(self):
        return self.tax_deduction + self.provident_fund + self.other_deductions

    @property
    def net_salary(self):
        return self.basic_salary + self.total_allowances - self.total_deductions


class EmployeeDocument(TimeStampedModel):
    DOCUMENT_TYPE_CHOICES = [
        ('id_card', 'ID Card'),
        ('passport', 'Passport'),
        ('contract', 'Contract'),
        ('certificate', 'Certificate'),
        ('resume', 'Resume'),
        ('other', 'Other'),
    ]

    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'employees_document'

    def __str__(self):
        return f'{self.employee.full_name} - {self.title}'

"""
DAYFLOW HRMS - Payroll models.
"""
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from apps.employees.models import EmployeeProfile


class Payroll(TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('processed', 'Processed'),
        ('paid', 'Paid'),
    ]

    MONTH_CHOICES = [(i, i) for i in range(1, 13)]

    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='payrolls')
    month = models.PositiveIntegerField(choices=MONTH_CHOICES)
    year = models.PositiveIntegerField()

    # Earnings
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    house_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    overtime_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Deductions
    tax_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    provident_fund = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unpaid_leave_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Attendance stats
    working_days = models.PositiveIntegerField(default=0)
    present_days = models.PositiveIntegerField(default=0)
    absent_days = models.PositiveIntegerField(default=0)
    leave_days = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='processed_payrolls'
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'payroll_record'
        unique_together = ['employee', 'month', 'year']
        ordering = ['-year', '-month']

    def __str__(self):
        return f'{self.employee.full_name} - {self.month}/{self.year}'

    @property
    def gross_salary(self):
        return (self.basic_salary + self.house_allowance + self.transport_allowance +
                self.medical_allowance + self.other_allowances + self.overtime_pay + self.bonus)

    @property
    def total_deductions(self):
        return (self.tax_deduction + self.provident_fund +
                self.unpaid_leave_deduction + self.other_deductions)

    @property
    def net_salary(self):
        return self.gross_salary - self.total_deductions

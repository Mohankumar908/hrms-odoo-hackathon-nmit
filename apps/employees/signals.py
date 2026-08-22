"""
Auto-create leave balances for new employees.
Auto-create a default SalaryStructure so payroll generation never silently fails.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


@receiver(post_save, sender='employees.EmployeeProfile')
def init_employee_data(sender, instance, created, **kwargs):
    if not created:
        return

    year = timezone.localdate().year

    # 1. Create a zero-value SalaryStructure so payroll generation doesn't fail
    try:
        from apps.employees.models import SalaryStructure
        SalaryStructure.objects.get_or_create(
            employee=instance,
            defaults={'effective_from': timezone.localdate()}
        )
    except Exception:
        pass

    # 2. Create LeaveBalance for every active LeaveType
    try:
        from apps.leave_management.models import LeaveType, LeaveBalance
        for lt in LeaveType.objects.filter(is_active=True):
            LeaveBalance.objects.get_or_create(
                employee=instance,
                leave_type=lt,
                year=year,
                defaults={'allocated_days': lt.max_days_per_year or 0, 'used_days': 0}
            )
    except Exception:
        pass

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Payroll


@login_required
def payroll_view(request):
    user = request.user
    if user.role in ('admin', 'hr'):
        payrolls = Payroll.objects.select_related('employee__user').all()
    else:
        payrolls = Payroll.objects.filter(employee__user=user)
    return render(request, 'payroll/payroll.html', {'payrolls': payrolls})

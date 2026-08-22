from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def reports_dashboard(request):
    if request.user.role not in ('admin', 'hr'):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    return render(request, 'reports/reports.html', {})

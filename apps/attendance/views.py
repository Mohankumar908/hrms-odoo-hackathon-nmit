from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from datetime import datetime
from .models import Attendance
from apps.employees.models import EmployeeProfile


@login_required
def attendance_view(request):
    user  = request.user
    today = timezone.localdate()
    try:    profile = user.employee_profile
    except: profile = None
    month = int(request.GET.get('month', today.month))
    year  = int(request.GET.get('year',  today.year))
    monthly   = Attendance.objects.filter(employee__user=user, date__month=month, date__year=year).order_by('-date') if profile else []
    today_att = Attendance.objects.filter(employee__user=user, date=today).first() if profile else None
    import calendar
    month_choices = [(i, calendar.month_name[i]) for i in range(1, 13)]
    return render(request, 'attendance/attendance.html', {
        'today_att': today_att, 'monthly': monthly,
        'month': month, 'year': year, 'today': today,
        'month_choices': month_choices,
    })


@login_required
def checkin_view(request):
    if request.method != 'POST': return redirect('attendance:attendance')
    user  = request.user
    today = timezone.localdate()
    try:    profile = user.employee_profile
    except EmployeeProfile.DoesNotExist:
        messages.error(request, 'No employee profile found.')
        return redirect('attendance:attendance')
    att, created = Attendance.objects.get_or_create(
        employee=profile, date=today,
        defaults={'status':'present','check_in':timezone.localtime().time(),
                  'check_in_ip':request.META.get('REMOTE_ADDR')}
    )
    if not created and att.check_in:
        messages.warning(request, 'Already checked in today.')
    else:
        if not created:
            att.check_in = timezone.localtime().time()
            att.status   = 'present'
            att.save()
        messages.success(request, f'Checked in at {att.check_in.strftime("%H:%M")}.')
    return redirect('attendance:attendance')


@login_required
def checkout_view(request):
    if request.method != 'POST': return redirect('attendance:attendance')
    user  = request.user
    today = timezone.localdate()
    try:    att = Attendance.objects.get(employee__user=user, date=today)
    except Attendance.DoesNotExist:
        messages.error(request, 'No check-in record for today.')
        return redirect('attendance:attendance')
    if att.check_out:
        messages.warning(request, 'Already checked out.')
    else:
        att.check_out = timezone.localtime().time()
        att.calculate_working_hours()
        att.save()
        messages.success(request, f'Checked out at {att.check_out.strftime("%H:%M")}. {att.working_hours}h worked.')
    return redirect('attendance:attendance')


@login_required
def admin_attendance_view(request):
    if request.user.role not in ('admin','hr'): raise PermissionDenied
    today    = timezone.localdate()
    date_str = request.GET.get('date', str(today))
    try:    view_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except: view_date = today
    records    = Attendance.objects.filter(date=view_date).select_related('employee__user','employee__department')
    all_active = EmployeeProfile.objects.filter(employment_status='active').count()
    return render(request, 'attendance/admin_attendance.html', {
        'records': records, 'today': today, 'view_date': view_date,
        'all_active': all_active,
        'present':  records.filter(status='present').count(),
        'absent':   records.filter(status='absent').count(),
        'on_leave': records.filter(status='leave').count(),
    })

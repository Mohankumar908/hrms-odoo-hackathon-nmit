from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification
from . import services

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user)
    if request.method == 'POST':
        services.mark_all_read(request.user)
    return render(request, 'notifications/notifications.html', {'notifications': notifications})

from django.urls import path
from . import api_views

app_name = 'api_notifications'

urlpatterns = [
    path('',                    api_views.NotificationListView.as_view(), name='list'),
    path('unread-count/',       api_views.unread_count,                   name='unread_count'),
    path('read-all/',           api_views.mark_all_read,                  name='mark_all_read'),
    path('clear-all/',          api_views.clear_all_notifications,        name='clear_all'),
    path('broadcast/',          api_views.broadcast_announcement,         name='broadcast'),
    path('<int:pk>/read/',      api_views.mark_read,                      name='mark_read'),
    path('<int:pk>/delete/',    api_views.delete_notification,            name='delete'),
]

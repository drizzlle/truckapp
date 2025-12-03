from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification_list'),
    path('<uuid:notification_id>/read/', views.MarkReadView.as_view(), name='notification_read'),
    path('devices/', views.RegisterDeviceView.as_view(), name='register_device'),
]


from django.contrib import admin
from .models import Notification, FCMDevice

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'is_push_sent', 'created_at')
    list_filter = ('notification_type', 'is_read', 'is_push_sent')
    search_fields = ('user__username', 'title', 'message')

@admin.register(FCMDevice)
class FCMDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_type', 'is_active', 'created_at')
    list_filter = ('device_type', 'is_active')
    search_fields = ('user__username',)


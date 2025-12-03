from rest_framework import generics, permissions, views, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.notifications.models import Notification, FCMDevice
from .serializers import NotificationSerializer, FCMDeviceSerializer

class NotificationListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user).order_by('-created_at')
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            qs = qs.filter(is_read=is_read.lower() == 'true')
        return qs
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True) if page is not None else self.get_serializer(queryset, many=True)
        
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        data = {
            "unread_count": unread_count,
            "results": serializer.data
        }
        return self.get_paginated_response(data['results']) if page is not None else Response(data)

class MarkReadView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, notification_id):
        notif = get_object_or_404(Notification, id=notification_id, user=request.user)
        notif.is_read = True
        notif.read_at = timezone.now() if hasattr(notif, 'read_at') else None # Check model
        notif.save()
        return Response({"message": "Notification marked as read"})

from django.utils import timezone # Added missing import

class RegisterDeviceView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FCMDeviceSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        FCMDevice.objects.update_or_create(
            user=request.user,
            device_token=serializer.validated_data['device_token'],
            defaults={'device_type': serializer.validated_data['device_type'], 'is_active': True}
        )
        
        return Response({"message": "Device registered successfully"}, status=status.HTTP_201_CREATED)


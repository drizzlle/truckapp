from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer, UserUpdateSerializer

User = get_user_model()

class MeView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_object(self):
        return self.request.user

class DriverProfileView(generics.RetrieveAPIView):
    """
    Public view to see driver details
    """
    permission_classes = [permissions.AllowAny] # Or IsAuthenticated depending on privacy policy
    serializer_class = UserSerializer
    queryset = User.objects.filter(user_type='driver')
    lookup_url_kwarg = 'driver_id'

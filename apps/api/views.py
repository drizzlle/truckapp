
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from . serializers import UserSerializer

User = get_user_model()

# Create your views here.
# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

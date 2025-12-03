from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.MeView.as_view(), name='user-me'),
    path('drivers/<uuid:driver_id>/', views.DriverProfileView.as_view(), name='driver-profile'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('available/', views.AvailableDriversView.as_view(), name='available-drivers'),
    path('toggle-availability/', views.ToggleAvailabilityView.as_view(), name='toggle-availability'),
    path('me/stats/', views.DriverStatsView.as_view(), name='driver-stats'),
    path('me/vehicle-photos/', views.VehiclePhotosView.as_view(), name='vehicle-photos'),
    path('me/vehicle-photos/<uuid:photo_id>/', views.VehiclePhotoDetailView.as_view(), name='vehicle-photo-detail'),
]

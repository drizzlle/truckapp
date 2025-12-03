from django.urls import path, include

urlpatterns = [
    path('auth/', include('apps.api.auth.urls')),
    path('users/', include('apps.api.users.urls')),
    path('config/', include('apps.api.configurations.urls')),
    path('jobs/', include('apps.api.jobs.urls')),
    path('drivers/', include('apps.api.drivers.urls')),
    path('ratings/', include('apps.api.ratings.urls')),
    path('payments/', include('apps.api.payments.urls')),
    path('notifications/', include('apps.api.notifications.urls')),
]

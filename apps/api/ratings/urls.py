from django.urls import path
from . import views

urlpatterns = [
    path('', views.RateUserView.as_view(), name='create_rating'),
    path('user/<uuid:user_id>/', views.UserRatingsView.as_view(), name='user_ratings'),
]


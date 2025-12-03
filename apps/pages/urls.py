from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api-docs/", views.api_docs, name="api-docs"),
]
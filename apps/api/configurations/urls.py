from django.urls import path
from . import views

urlpatterns = [
    path('vehicle-types/', views.VehicleTypeListView.as_view(), name='vehicle-type-list'),
    path('item-categories/', views.ItemCategoryListView.as_view(), name='item-category-list'),
    path('calculate-price/', views.CalculatePriceView.as_view(), name='calculate-price'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.JobListCreateView.as_view(), name='job_list_create'),
    path('requests/', views.DriverJobRequestsView.as_view(), name='driver_job_requests'),
    path('<uuid:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('<uuid:pk>/accept/', views.AcceptJobView.as_view(), name='job_accept'),
    path('<uuid:pk>/reject/', views.RejectJobView.as_view(), name='job_reject'),
    path('<uuid:pk>/driver-confirm-pickup/', views.DriverConfirmPickupView.as_view(), name='driver_confirm_pickup'),
    path('<uuid:pk>/customer-confirm-pickup/', views.CustomerConfirmPickupView.as_view(), name='customer_confirm_pickup'),
    path('<uuid:pk>/start-delivery/', views.StartDeliveryView.as_view(), name='start_delivery'),
    path('<uuid:pk>/mark-delivered/', views.MarkDeliveredView.as_view(), name='mark_delivered'),
    path('<uuid:pk>/confirm-delivery/', views.ConfirmDeliveryView.as_view(), name='confirm_delivery'),
    path('<uuid:pk>/cancel/', views.CancelJobView.as_view(), name='cancel_job'),
    path('<uuid:pk>/dispute/', views.DisputeJobView.as_view(), name='dispute_job'),
    path('<uuid:pk>/update-location/', views.UpdateLocationView.as_view(), name='update_location'),
]


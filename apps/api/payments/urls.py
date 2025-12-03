from django.urls import path
from . import views

urlpatterns = [
    path('', views.PaymentHistoryView.as_view(), name='payment_history'),
    path('initialize/<uuid:job_id>/', views.InitializePaymentView.as_view(), name='payment_initialize'),
    path('verify/<str:reference>/', views.PaymentVerificationView.as_view(), name='payment_verify'),
]


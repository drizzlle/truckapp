from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/customer/', views.CustomerRegistrationView.as_view(), name='register-customer'),
    path('register/driver/', views.DriverRegistrationView.as_view(), name='register-driver'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('phone/verify/request/', views.RequestPhoneVerificationView.as_view(), name='phone-verify-request'),
    path('phone/verify/confirm/', views.ConfirmPhoneVerificationView.as_view(), name='phone-verify-confirm'),
    path('password/reset/request/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('password/change/', views.ChangePasswordView.as_view(), name='password-change'),
    path('email/verify/request/', views.RequestEmailVerificationView.as_view(), name='email-verify-request'),
    path('email/verify/confirm/', views.ConfirmEmailVerificationView.as_view(), name='email-verify-confirm'),
]

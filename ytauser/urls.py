from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminUserViewSet, CreateAccountWithEmptyPasswordView, CreateUserEmailView, CreateUserView, LoginUserView, LogoutAPIView, OTPEmailLoginView, OTPLoginView, ProfileViewSet, ResendOTPView, SendOTPView, UserActivityViewSet, RewardViewSet, VerifyOTPView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)   


# Router for ModelViewSet
router = DefaultRouter()
router.register('profiles', ProfileViewSet,'profiles')
router.register('user_activities', UserActivityViewSet,'activities')
router.register('rewards', RewardViewSet,'rewards')
router.register('get-user', AdminUserViewSet, basename='get-user')  

urlpatterns = [
    path('create_user/', CreateUserView.as_view(), name='create_user'),
    path('create_email_user/', CreateUserEmailView.as_view(), name='create_email_user'),
    path('login/', LoginUserView.as_view(), name='login_user'),
    path('otp-login/', OTPLoginView.as_view(), name='otp_login'),
    path('email-otp-login/', OTPEmailLoginView.as_view(), name='email_otp_login'),
    path('otp-create_user/', CreateAccountWithEmptyPasswordView.as_view(), name='create_user_by_otp'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('send/', SendOTPView.as_view(), name='send_otp'),
    path('verify/', VerifyOTPView.as_view(), name='verify_otp'),
    path('resend/', ResendOTPView.as_view(), name='resend_otp'),
    # path('get-users/', AdminUserViewSet.as_view(), name='get-users'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('', include(router.urls)),  # Includes the ModelViewSet URLs
]
  
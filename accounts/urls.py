from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    PhonePasswordLoginView,
    PhoneCodeLoginView,
    SendVerificationCodeView,
    UserProfileView,
    WechatLoginUrlView,
    WechatCallbackView,
    BindPhoneView
)

urlpatterns = [
    # 注册和登录
    path('register/', RegisterView.as_view(), name='register'),
    path('login/phone-password/', PhonePasswordLoginView.as_view(), name='phone-password-login'),
    path('login/phone-code/', PhoneCodeLoginView.as_view(), name='phone-code-login'),
    path('send-code/', SendVerificationCodeView.as_view(), name='send-verification-code'),

    # 微信登录
    path('wechat/login-url/', WechatLoginUrlView.as_view(), name='wechat-login-url'),
    path('wechat/callback/', WechatCallbackView.as_view(), name='wechat-callback'),
    
    # 账号互通
    path('bind-phone/', BindPhoneView.as_view(), name='bind-phone'),

    # JWT令牌刷新
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # 用户信息
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]

from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from backend.utils import api_success_response, api_error_response
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    PhonePasswordLoginSerializer,
    PhoneCodeLoginSerializer,
    SendVerificationCodeSerializer,
    WechatLoginUrlSerializer,
    WechatCallbackSerializer
)
from .sms import send_verification_code

User = get_user_model()

class RegisterView(APIView):
    """
    用户注册视图
    ---
    post:
        描述: 使用手机号和验证码注册新用户
        参数:
            - name: phone
              description: 手机号
              required: true
              type: string
            - name: code
              description: 验证码
              required: true
              type: string
            - name: password
              description: 密码
              required: true
              type: string
            - name: username
              description: 用户名（可选）
              required: false
              type: string
        响应:
            200:
                描述: 注册成功
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return api_success_response(
                data={'user': UserSerializer(user).data},
                message='注册成功',
                status=status.HTTP_201_CREATED
            )
        return api_error_response(
            code=1006,
            message='注册失败',
            status=status.HTTP_400_BAD_REQUEST
        )

class PhonePasswordLoginView(APIView):
    """手机号密码登录视图"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PhonePasswordLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            return api_success_response(
                data={
                    'user': UserSerializer(serializer.validated_data['user']).data,
                    'refresh': serializer.validated_data['refresh'],
                    'access': serializer.validated_data['access']
                },
                message='登录成功'
            )
        return api_error_response(
            code=1001,
            message='登录失败',
            status=status.HTTP_400_BAD_REQUEST
        )

class PhoneCodeLoginView(APIView):
    """手机号验证码登录视图"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PhoneCodeLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            is_new_user = serializer.validated_data.get('is_new_user', False)
            return api_success_response(
                data={
                    'user': UserSerializer(serializer.validated_data['user']).data,
                    'refresh': serializer.validated_data['refresh'],
                    'access': serializer.validated_data['access'],
                    'is_new_user': is_new_user
                },
                message='登录成功'
            )
        return api_error_response(
            code=1001,
            message='登录失败',
            status=status.HTTP_400_BAD_REQUEST
        )

class SendVerificationCodeView(APIView):
    """发送验证码视图"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SendVerificationCodeSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            purpose = serializer.validated_data['purpose']

            success, verification = send_verification_code(phone, purpose)

            if success:
                return api_success_response(
                    data={'expires_at': verification.expires_at},
                    message='验证码发送成功'
                )
            else:
                return api_error_response(
                    code=2001,
                    message='验证码发送失败',
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return api_error_response(
            code=1006,
            message='验证码发送失败',
            status=status.HTTP_400_BAD_REQUEST
        )

class UserProfileView(APIView):
    """用户信息视图"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return api_success_response(
            data={'user': serializer.data},
            message='获取用户信息成功'
        )

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return api_success_response(
                data={'user': serializer.data},
                message='更新用户信息成功'
            )
        return api_error_response(
            code=1006,
            message='更新用户信息失败',
            status=status.HTTP_400_BAD_REQUEST
        )

class WechatLoginUrlView(APIView):
    """获取微信登录URL视图"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = WechatLoginUrlSerializer(data=request.data)
        if serializer.is_valid():
            return api_success_response(
                data={
                    'login_url': serializer.validated_data['login_url'],
                    'state': serializer.validated_data['state']
                },
                message='获取微信登录URL成功'
            )
        return api_error_response(
            code=1006,
            message='获取微信登录URL失败',
            status=status.HTTP_400_BAD_REQUEST
        )

class WechatCallbackView(APIView):
    """微信登录回调视图"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # 微信回调会将code和state作为GET参数传递
        serializer = WechatCallbackSerializer(data=request.query_params, context={'request': request})
        if serializer.is_valid():
            # 重定向到前端页面，并带上JWT令牌和用户信息
            redirect_url = serializer.validated_data['redirect_url']
            access_token = serializer.validated_data['access']
            refresh_token = serializer.validated_data['refresh']
            is_new_user = serializer.validated_data['is_new_user']

            # 构建重定向URL，带上令牌和用户信息
            redirect_url = f"{redirect_url}?access_token={access_token}&refresh_token={refresh_token}&is_new_user={is_new_user}"

            return api_success_response(
                data={'redirect_url': redirect_url},
                message='微信登录成功'
            )
        return api_error_response(
            code=1001,
            message='微信登录失败',
            status=status.HTTP_400_BAD_REQUEST
        )

    def post(self, request):
        # 允许前端直接调用该接口，而不通过微信回调
        serializer = WechatCallbackSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            return api_success_response(
                data={
                    'user': UserSerializer(serializer.validated_data['user']).data,
                    'refresh': serializer.validated_data['refresh'],
                    'access': serializer.validated_data['access'],
                    'is_new_user': serializer.validated_data['is_new_user']
                },
                message='微信登录成功'
            )
        return api_error_response(
            code=1001,
            message='微信登录失败',
            status=status.HTTP_400_BAD_REQUEST
        )
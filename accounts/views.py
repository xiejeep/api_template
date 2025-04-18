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
    """
    手机号密码登录视图
    ---
    post:
        描述: 使用手机号和密码登录
        参数:
            - name: phone
              description: 手机号
              required: true
              type: string
              example: "+8613800138000"
            - name: password
              description: 密码
              required: true
              type: string
              example: "password123"
        响应:
            200:
                描述: 登录成功
                示例:
                    {
                        "code": 0,
                        "message": "登录成功",
                        "data": {
                            "user": {
                                "id": 1,
                                "username": "user123",
                                "phone": "+8613800138000",
                                "email": null,
                                "is_phone_verified": true,
                                "date_joined": "2025-04-18T12:00:00Z"
                            },
                            "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                        },
                        "pagination": null
                    }
            400:
                描述: 登录失败
                示例:
                    {
                        "code": 1001,
                        "message": "登录失败",
                        "data": null,
                        "pagination": null
                    }
    """
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
    """
    手机号验证码登录视图
    ---
    post:
        描述: 使用手机号和验证码登录
        参数:
            - name: phone
              description: 手机号
              required: true
              type: string
              example: "+8613800138000"
            - name: code
              description: 验证码
              required: true
              type: string
              example: "123456"
        响应:
            200:
                描述: 登录成功
                示例:
                    {
                        "code": 0,
                        "message": "登录成功",
                        "data": {
                            "user": {
                                "id": 1,
                                "username": "user123",
                                "phone": "+8613800138000",
                                "email": null,
                                "is_phone_verified": true,
                                "date_joined": "2025-04-18T12:00:00Z"
                            },
                            "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "is_new_user": false
                        },
                        "pagination": null
                    }
            400:
                描述: 登录失败
                示例:
                    {
                        "code": 1001,
                        "message": "登录失败",
                        "data": null,
                        "pagination": null
                    }
    """
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
    """
    发送验证码视图
    ---
    post:
        描述: 发送手机验证码
        参数:
            - name: phone
              description: 手机号
              required: true
              type: string
              example: "+8613800138000"
            - name: purpose
              description: 用途，可选值：register(注册), login(登录), reset_password(重置密码)
              required: true
              type: string
              example: "register"
        响应:
            200:
                描述: 验证码发送成功
                示例:
                    {
                        "code": 0,
                        "message": "验证码发送成功",
                        "data": {
                            "expires_at": "2025-04-18T12:10:00Z"
                        },
                        "pagination": null
                    }
            400:
                描述: 验证码发送失败
                示例:
                    {
                        "code": 1006,
                        "message": "验证码发送失败",
                        "data": null,
                        "pagination": null
                    }
            500:
                描述: 服务器错误
                示例:
                    {
                        "code": 2001,
                        "message": "验证码发送失败",
                        "data": null,
                        "pagination": null
                    }
    """
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
    """
    用户信息视图
    ---
    get:
        描述: 获取当前登录用户的信息
        响应:
            200:
                描述: 获取用户信息成功
                示例:
                    {
                        "code": 0,
                        "message": "获取用户信息成功",
                        "data": {
                            "user": {
                                "id": 1,
                                "username": "user123",
                                "phone": "+8613800138000",
                                "email": "user@example.com",
                                "is_phone_verified": true,
                                "date_joined": "2025-04-18T12:00:00Z"
                            }
                        },
                        "pagination": null
                    }
            401:
                描述: 未认证
                示例:
                    {
                        "code": 1002,
                        "message": "未认证",
                        "data": null,
                        "pagination": null
                    }
    patch:
        描述: 更新当前登录用户的信息
        参数:
            - name: username
              description: 用户名
              required: false
              type: string
              example: "new_username"
            - name: email
              description: 邮箱
              required: false
              type: string
              example: "user@example.com"
        响应:
            200:
                描述: 更新用户信息成功
                示例:
                    {
                        "code": 0,
                        "message": "更新用户信息成功",
                        "data": {
                            "user": {
                                "id": 1,
                                "username": "new_username",
                                "phone": "+8613800138000",
                                "email": "user@example.com",
                                "is_phone_verified": true,
                                "date_joined": "2025-04-18T12:00:00Z"
                            }
                        },
                        "pagination": null
                    }
            400:
                描述: 更新用户信息失败
                示例:
                    {
                        "code": 1006,
                        "message": "更新用户信息失败",
                        "data": null,
                        "pagination": null
                    }
            401:
                描述: 未认证
                示例:
                    {
                        "code": 1002,
                        "message": "未认证",
                        "data": null,
                        "pagination": null
                    }
    """
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
    """
    获取微信登录URL视图
    ---
    post:
        描述: 获取微信登录URL和状态码
        参数:
            - name: redirect_url
              description: 登录成功后重定向的URL
              required: true
              type: string
              example: "http://localhost:3000/auth/callback"
        响应:
            200:
                描述: 获取微信登录URL成功
                示例:
                    {
                        "code": 0,
                        "message": "获取微信登录URL成功",
                        "data": {
                            "login_url": "https://open.weixin.qq.com/connect/qrconnect?appid=wx123456789&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fapi%2Fauth%2Fwechat%2Fcallback&response_type=code&scope=snsapi_login&state=abcdef123456#wechat_redirect",
                            "state": "abcdef123456"
                        },
                        "pagination": null
                    }
            400:
                描述: 获取微信登录URL失败
                示例:
                    {
                        "code": 1006,
                        "message": "获取微信登录URL失败",
                        "data": null,
                        "pagination": null
                    }
    """
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
    """
    微信登录回调视图
    ---
    get:
        描述: 处理微信登录回调，由微信服务器调用
        参数:
            - name: code
              description: 微信授权临时票据
              required: true
              type: string
              example: "021ABC"
            - name: state
              description: 状态码，用于防止CSRF攻击
              required: true
              type: string
              example: "abcdef123456"
        响应:
            200:
                描述: 微信登录成功，返回重定向URL
                示例:
                    {
                        "code": 0,
                        "message": "微信登录成功",
                        "data": {
                            "redirect_url": "http://localhost:3000/auth/callback?access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...&refresh_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...&is_new_user=false"
                        },
                        "pagination": null
                    }
            400:
                描述: 微信登录失败
                示例:
                    {
                        "code": 1001,
                        "message": "微信登录失败",
                        "data": null,
                        "pagination": null
                    }
    post:
        描述: 处理微信登录，由前端直接调用
        参数:
            - name: code
              description: 微信授权临时票据
              required: true
              type: string
              example: "021ABC"
            - name: state
              description: 状态码，用于防止CSRF攻击
              required: true
              type: string
              example: "abcdef123456"
        响应:
            200:
                描述: 微信登录成功
                示例:
                    {
                        "code": 0,
                        "message": "微信登录成功",
                        "data": {
                            "user": {
                                "id": 1,
                                "username": "wx_12345678",
                                "phone": null,
                                "email": null,
                                "is_phone_verified": false,
                                "date_joined": "2025-04-18T12:00:00Z"
                            },
                            "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "is_new_user": true
                        },
                        "pagination": null
                    }
            400:
                描述: 微信登录失败
                示例:
                    {
                        "code": 1001,
                        "message": "微信登录失败",
                        "data": null,
                        "pagination": null
                    }
    """
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
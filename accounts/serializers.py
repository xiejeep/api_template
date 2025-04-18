from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
import phonenumbers
from .models import VerificationCode
from .sms import verify_code
from .wechat import wechat_login, wechat_mini_login, WechatLoginError
from django.core.validators import RegexValidator
from django.conf import settings
from django.db import transaction
import requests
import uuid
import base64
import json
import datetime
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class PhoneNumberField(serializers.CharField):
    """手机号字段验证器"""

    def to_internal_value(self, data):
        phone_number = super().to_internal_value(data)
        try:
            # 解析手机号
            parsed_number = phonenumbers.parse(phone_number, "CN")
            # 验证手机号是否有效
            if not phonenumbers.is_valid_number(parsed_number):
                raise serializers.ValidationError(_("无效的手机号码"))
            # 返回标准格式的手机号
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError(_("无效的手机号码格式"))

class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""

    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'email', 'is_phone_verified', 'date_joined', 'last_login', 'wechat_nickname', 'wechat_avatar']
        read_only_fields = ['id', 'is_phone_verified', 'date_joined', 'last_login', 'wechat_nickname', 'wechat_avatar']

class RegisterSerializer(serializers.Serializer):
    """注册序列化器"""

    phone = PhoneNumberField(required=True)
    code = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True, min_length=8)
    username = serializers.CharField(required=False)

    def validate(self, attrs):
        phone = attrs.get('phone')
        code = attrs.get('code')

        # 验证验证码
        is_valid, message = verify_code(phone, code, 'register')
        if not is_valid:
            raise serializers.ValidationError({"code": message})

        # 检查手机号是否已注册
        if User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({"phone": _("该手机号已注册")})

        return attrs

    def create(self, validated_data):
        phone = validated_data.get('phone')
        password = validated_data.get('password')
        username = validated_data.get('username')

        # 创建用户
        user = User.objects.create_user(
            phone=phone,
            username=username,
            password=password,
            is_phone_verified=True
        )

        return user

class PhonePasswordLoginSerializer(serializers.Serializer):
    """手机号密码登录序列化器"""

    phone = PhoneNumberField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')

        # 查找用户
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError({"phone": _("该手机号未注册")})

        # 验证密码
        if not user.check_password(password):
            raise serializers.ValidationError({"password": _("密码错误")})

        # 获取客户端IP
        request = self.context.get('request')
        if request:
            user.last_login_ip = self.get_client_ip(request)
            user.save(update_fields=['last_login_ip'])

        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)

        return {
            'user': user,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class PhoneCodeLoginSerializer(serializers.Serializer):
    """手机号验证码登录序列化器"""

    phone = PhoneNumberField(required=True)
    code = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        phone = attrs.get('phone')
        code = attrs.get('code')

        # 验证验证码
        is_valid, message = verify_code(phone, code, 'login')
        if not is_valid:
            raise serializers.ValidationError({"code": message})

        # 查找或创建用户
        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={
                'is_phone_verified': True
            }
        )

        # 获取客户端IP
        request = self.context.get('request')
        if request:
            user.last_login_ip = self.get_client_ip(request)
            user.save(update_fields=['last_login_ip'])

        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)

        return {
            'user': user,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'is_new_user': created
        }

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class SendVerificationCodeSerializer(serializers.Serializer):
    """发送验证码序列化器"""

    phone = PhoneNumberField(required=True)
    purpose = serializers.ChoiceField(
        choices=['register', 'login', 'reset_password', 'bind_phone'],
        required=True
    )

    def validate(self, attrs):
        phone = attrs.get('phone')
        purpose = attrs.get('purpose')

        # 检查是否频繁发送
        last_code = VerificationCode.objects.filter(
            phone=phone,
            purpose=purpose
        ).order_by('-created_at').first()

        if last_code and (timezone.now() - last_code.created_at).total_seconds() < 60:
            raise serializers.ValidationError({"phone": _("发送过于频繁，请稍后再试")})

        # 如果是注册，检查手机号是否已注册
        if purpose == 'register' and User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({"phone": _("该手机号已注册")})

        # 如果是登录或重置密码，检查手机号是否已注册
        if purpose in ['login', 'reset_password'] and not User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({"phone": _("该手机号未注册")})

        # 对于bind_phone用途，不需要额外验证

        return attrs

class WechatLoginUrlSerializer(serializers.Serializer):
    """获取微信登录URL序列化器"""

    redirect_url = serializers.URLField(required=True)

    def validate(self, attrs):
        redirect_url = attrs.get('redirect_url')

        try:
            # 获取微信登录URL
            login_url, state = wechat_login.get_login_url(redirect_url)

            return {
                'login_url': login_url,
                'state': state
            }
        except Exception as e:
            raise serializers.ValidationError({'redirect_url': str(e)})

class WechatCallbackSerializer(serializers.Serializer):
    """微信回调序列化器"""

    code = serializers.CharField(required=True)
    state = serializers.CharField(required=True)

    def validate(self, attrs):
        code = attrs.get('code')
        state = attrs.get('state')

        try:
            # 验证状态码
            state_obj = wechat_login.validate_state(state)

            # 获取访问令牌
            token_info = wechat_login.get_access_token(code)
            access_token = token_info.get('access_token')
            openid = token_info.get('openid')
            unionid = token_info.get('unionid')

            # 获取用户信息
            user_info = wechat_login.get_user_info(access_token, openid)

            # 查找或创建用户
            user = None
            is_new_user = False

            # 先尝试使用unionid查找用户
            if unionid:
                try:
                    user = User.objects.get(wechat_unionid=unionid)
                except User.DoesNotExist:
                    pass

            # 如果没找到，尝试使用openid查找用户
            if not user:
                try:
                    user = User.objects.get(wechat_openid=openid)
                except User.DoesNotExist:
                    pass

            # 如果还是没找到，创建新用户
            if not user:
                username = f"wx_{openid[:8]}"
                user = User.objects.create_user(
                    username=username,
                    wechat_openid=openid,
                    wechat_unionid=unionid,
                    wechat_nickname=user_info.get('nickname'),
                    wechat_avatar=user_info.get('headimgurl')
                )
                is_new_user = True
            else:
                # 更新用户信息
                user.wechat_openid = openid
                user.wechat_unionid = unionid
                user.wechat_nickname = user_info.get('nickname')
                user.wechat_avatar = user_info.get('headimgurl')
                user.save(update_fields=['wechat_openid', 'wechat_unionid', 'wechat_nickname', 'wechat_avatar'])

            # 获取客户端IP
            request = self.context.get('request')
            if request:
                user.last_login_ip = self.get_client_ip(request)
                user.save(update_fields=['last_login_ip'])

            # 生成JWT令牌
            refresh = RefreshToken.for_user(user)

            return {
                'user': user,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'is_new_user': is_new_user,
                'redirect_url': state_obj.redirect_url,
                'needs_phone_binding': is_new_user and not user.phone  # 新用户且没有手机号需要绑定
            }
        except WechatLoginError as e:
            raise serializers.ValidationError({'code': str(e)})
        except Exception as e:
            raise serializers.ValidationError({'code': f"微信登录失败: {str(e)}"})

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class BindPhoneSerializer(serializers.Serializer):
    """绑定手机号序列化器"""

    phone = PhoneNumberField(required=True)
    code = serializers.CharField(required=True)
    merge_accounts = serializers.BooleanField(default=False)

    def validate(self, attrs):
        phone = attrs.get('phone')
        code = attrs.get('code')
        merge_accounts = attrs.get('merge_accounts')
        user = self.context['request'].user

        # 验证验证码
        is_valid, message = verify_code(phone, code, 'bind_phone')
        if not is_valid:
            raise serializers.ValidationError({"code": message})

        # 检查手机号是否已被其他账号使用
        existing_user = User.objects.filter(phone=phone).first()
        if existing_user and existing_user.id != user.id:
            if not merge_accounts:
                raise serializers.ValidationError({
                    "phone": _("该手机号已被其他账号使用"),
                    "existing_user": True
                })

            # 如果选择合并账号，需要将现有账号的信息合并到当前账号
            # 这里只是一个简单的示例，实际合并逻辑可能更复杂
            if not user.wechat_openid and existing_user.wechat_openid:
                user.wechat_openid = existing_user.wechat_openid
                user.wechat_unionid = existing_user.wechat_unionid
                user.wechat_nickname = existing_user.wechat_nickname
                user.wechat_avatar = existing_user.wechat_avatar

            # 删除现有账号（或者标记为已合并）
            existing_user.delete()

        return attrs

    def update(self, instance, validated_data):
        phone = validated_data.get('phone')

        # 更新用户手机号
        instance.phone = phone
        instance.is_phone_verified = True
        instance.save(update_fields=['phone', 'is_phone_verified'])

        return instance

class WechatMiniLoginSerializer(serializers.Serializer):
    """微信小程序登录序列化器"""
    code = serializers.CharField(required=True, help_text='微信小程序临时登录凭证')
    
    def validate(self, attrs):
        """
        验证登录凭证并获取用户信息
        """
        code = attrs.get('code')
        
        try:
            # 获取微信小程序会话信息
            session_info = wechat_mini_login.get_session_info(code)
            
            # 获取用户唯一标识
            openid = session_info.get('openid')
            unionid = session_info.get('unionid')
            
            if not openid:
                raise serializers.ValidationError('获取微信用户信息失败')
            
            # 查找或创建用户
            user = None
            
            # 优先通过unionid查找用户
            if unionid:
                try:
                    user = User.objects.filter(wechat_unionid=unionid).first()
                except User.DoesNotExist:
                    pass
            
            # 通过openid查找用户
            if not user:
                try:
                    user = User.objects.filter(wechat_openid=openid).first()
                except User.DoesNotExist:
                    pass
            
            is_new_user = False
            
            # 创建新用户
            if not user:
                is_new_user = True
                user = User.objects.create(
                    wechat_openid=openid,
                    wechat_unionid=unionid,
                    username=f'微信用户_{openid[:8]}',
                )
            else:
                # 更新用户的openid和unionid
                update_fields = []
                if not user.wechat_openid and openid:
                    user.wechat_openid = openid
                    update_fields.append('wechat_openid')
                if not user.wechat_unionid and unionid:
                    user.wechat_unionid = unionid
                    update_fields.append('wechat_unionid')
                if update_fields:
                    user.save(update_fields=update_fields)
            
            # 生成JWT令牌
            refresh = RefreshToken.for_user(user)
            
            data = {
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'is_new_user': is_new_user,
                'needs_phone_binding': not user.phone
            }
            
            return data
        except WechatLoginError as e:
            raise serializers.ValidationError(str(e))
        except Exception as e:
            logger.exception(f"微信小程序登录异常: {str(e)}")
            raise serializers.ValidationError(f"微信小程序登录异常: {str(e)}")
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

class UserManager(BaseUserManager):
    """自定义用户管理器"""

    def create_user(self, phone=None, username=None, email=None, password=None, **extra_fields):
        """创建普通用户"""
        if not phone and not username and not email:
            raise ValueError(_('必须提供手机号、用户名或邮箱之一'))

        if not username:
            username = str(uuid.uuid4())[:8]  # 生成随机用户名

        user = self.model(
            phone=phone,
            username=username,
            email=self.normalize_email(email) if email else None,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """创建超级用户"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('超级用户必须设置is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('超级用户必须设置is_superuser=True'))

        return self.create_user(username=username, password=password, **extra_fields)

class User(AbstractUser):
    """自定义用户模型"""
    phone = models.CharField(_('手机号'), max_length=20, unique=True, null=True, blank=True)
    is_phone_verified = models.BooleanField(_('手机号已验证'), default=False)
    email = models.EmailField(_('email address'), blank=True, null=True)
    date_joined = models.DateTimeField(_('注册时间'), default=timezone.now)
    last_login_ip = models.GenericIPAddressField(_('最后登录IP'), null=True, blank=True)

    # 微信相关字段
    wechat_openid = models.CharField(_('微信OpenID'), max_length=100, unique=True, null=True, blank=True)
    wechat_unionid = models.CharField(_('微信UnionID'), max_length=100, unique=True, null=True, blank=True)
    wechat_nickname = models.CharField(_('微信昵称'), max_length=100, null=True, blank=True)
    wechat_avatar = models.URLField(_('微信头像'), max_length=500, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')

    def __str__(self):
        return self.username or self.phone or self.email

class VerificationCode(models.Model):
    """验证码模型"""
    phone = models.CharField(_('手机号'), max_length=20)
    code = models.CharField(_('验证码'), max_length=10)
    purpose = models.CharField(_('用途'), max_length=20, choices=[
        ('register', _('注册')),
        ('login', _('登录')),
        ('reset_password', _('重置密码')),
    ])
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    expires_at = models.DateTimeField(_('过期时间'))
    is_used = models.BooleanField(_('是否已使用'), default=False)

    class Meta:
        verbose_name = _('验证码')
        verbose_name_plural = _('验证码')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.phone} - {self.code} ({self.purpose})"

    @property
    def is_expired(self):
        """检查验证码是否过期"""
        return timezone.now() > self.expires_at

class WechatLoginState(models.Model):
    """微信登录状态模型"""
    state = models.CharField(_('状态码'), max_length=100, unique=True)
    redirect_url = models.URLField(_('重定向URL'), max_length=500)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    expires_at = models.DateTimeField(_('过期时间'))
    is_used = models.BooleanField(_('是否已使用'), default=False)

    class Meta:
        verbose_name = _('微信登录状态')
        verbose_name_plural = _('微信登录状态')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.state} ({self.created_at})"

    @property
    def is_expired(self):
        """检查状态是否过期"""
        return timezone.now() > self.expires_at

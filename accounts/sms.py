import random
import logging
from abc import ABC, abstractmethod
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .models import VerificationCode

logger = logging.getLogger(__name__)

class SMSService(ABC):
    """短信服务抽象基类"""

    @abstractmethod
    def send_verification_code(self, phone, code, purpose):
        """发送验证码"""
        pass

class DevelopmentSMSService(SMSService):
    """开发环境短信服务，不实际发送短信，只打印到控制台"""

    def send_verification_code(self, phone, code, purpose):
        """发送验证码（仅打印到控制台）"""
        logger.info(f"[开发环境] 向 {phone} 发送验证码: {code}，用途: {purpose}")
        return True

class ThirdPartySMSService(SMSService):
    """第三方短信服务接口"""

    def __init__(self, api_key=None, api_secret=None):
        self.api_key = api_key or settings.SMS_API_KEY
        self.api_secret = api_secret or settings.SMS_API_SECRET

    def send_verification_code(self, phone, code, purpose):
        """发送验证码（实际调用第三方API）"""
        # 这里实现第三方短信API的调用
        # 例如：使用requests库调用API
        logger.info(f"[第三方服务] 向 {phone} 发送验证码: {code}，用途: {purpose}")

        # 模拟API调用
        # response = requests.post(
        #     'https://api.sms-service.com/send',
        #     json={
        #         'phone': phone,
        #         'message': f'您的验证码是: {code}，用途: {purpose}，5分钟内有效',
        #         'api_key': self.api_key,
        #         'api_secret': self.api_secret
        #     }
        # )
        # return response.status_code == 200

        # 开发环境下，假设发送成功
        return True

def get_sms_service():
    """获取短信服务实例"""
    if settings.DEBUG:
        return DevelopmentSMSService()
    else:
        return ThirdPartySMSService()

def generate_verification_code(length=6):
    """生成指定长度的数字验证码"""
    # 开发环境下使用固定验证码
    if settings.DEBUG:
        return '123456'
    return ''.join(random.choice('0123456789') for _ in range(length))

def send_verification_code(phone, purpose, expiry_minutes=5):
    """发送验证码并保存到数据库"""
    # 生成验证码
    code = generate_verification_code()

    # 计算过期时间
    expires_at = timezone.now() + timedelta(minutes=expiry_minutes)

    # 保存到数据库
    verification = VerificationCode.objects.create(
        phone=phone,
        code=code,
        purpose=purpose,
        expires_at=expires_at
    )

    # 发送验证码
    sms_service = get_sms_service()
    success = sms_service.send_verification_code(phone, code, purpose)

    return success, verification

def verify_code(phone, code, purpose):
    """验证验证码是否有效"""
    # 查找最近的未使用的验证码
    try:
        verification = VerificationCode.objects.filter(
            phone=phone,
            code=code,
            purpose=purpose,
            is_used=False
        ).latest('created_at')

        # 检查是否过期
        if verification.is_expired:
            return False, "验证码已过期"

        # 标记为已使用
        verification.is_used = True
        verification.save()

        return True, "验证成功"
    except VerificationCode.DoesNotExist:
        return False, "验证码无效或已使用"

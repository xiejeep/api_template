import requests
import logging
import uuid
import json
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from .models import WechatLoginState

logger = logging.getLogger(__name__)

class WechatLoginError(Exception):
    """微信登录错误"""
    pass

class WechatLogin:
    """微信登录工具类"""
    
    # 微信授权API地址
    OAUTH2_URL = 'https://open.weixin.qq.com/connect/qrconnect'
    # 获取访问令牌API地址
    ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    # 获取用户信息API地址
    USER_INFO_URL = 'https://api.weixin.qq.com/sns/userinfo'
    
    def __init__(self):
        """初始化微信登录工具类"""
        self.app_id = getattr(settings, 'WECHAT_APP_ID', '')
        self.app_secret = getattr(settings, 'WECHAT_APP_SECRET', '')
        
        if not self.app_id or not self.app_secret:
            logger.warning("微信登录配置缺失，请在settings.py中设置WECHAT_APP_ID和WECHAT_APP_SECRET")
    
    def get_login_url(self, redirect_url, scope='snsapi_login'):
        """
        获取微信登录URL
        
        Args:
            redirect_url: 授权后重定向的回调链接地址
            scope: 应用授权作用域，默认为snsapi_login
            
        Returns:
            login_url: 微信登录URL
            state: 随机生成的状态码
        """
        # 生成随机状态码
        state = str(uuid.uuid4())
        
        # 保存状态码和重定向URL
        expires_at = timezone.now() + timedelta(minutes=10)
        WechatLoginState.objects.create(
            state=state,
            redirect_url=redirect_url,
            expires_at=expires_at
        )
        
        # 构建微信登录URL
        params = {
            'appid': self.app_id,
            'redirect_uri': settings.WECHAT_REDIRECT_URI,
            'response_type': 'code',
            'scope': scope,
            'state': state
        }
        
        # 构建URL
        url_parts = []
        for key, value in params.items():
            url_parts.append(f"{key}={value}")
        
        login_url = f"{self.OAUTH2_URL}?{'&'.join(url_parts)}#wechat_redirect"
        
        return login_url, state
    
    def get_access_token(self, code):
        """
        获取微信访问令牌
        
        Args:
            code: 授权临时票据
            
        Returns:
            access_token: 访问令牌
            openid: 用户唯一标识
            其他返回参数
        """
        params = {
            'appid': self.app_id,
            'secret': self.app_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        
        try:
            response = requests.get(self.ACCESS_TOKEN_URL, params=params)
            result = response.json()
            
            if 'errcode' in result:
                logger.error(f"获取微信访问令牌失败: {result}")
                raise WechatLoginError(f"获取微信访问令牌失败: {result.get('errmsg', '未知错误')}")
            
            return result
        except Exception as e:
            logger.exception(f"获取微信访问令牌异常: {str(e)}")
            raise WechatLoginError(f"获取微信访问令牌异常: {str(e)}")
    
    def get_user_info(self, access_token, openid):
        """
        获取微信用户信息
        
        Args:
            access_token: 访问令牌
            openid: 用户唯一标识
            
        Returns:
            用户信息
        """
        params = {
            'access_token': access_token,
            'openid': openid,
            'lang': 'zh_CN'
        }
        
        try:
            response = requests.get(self.USER_INFO_URL, params=params)
            result = response.json()
            
            if 'errcode' in result:
                logger.error(f"获取微信用户信息失败: {result}")
                raise WechatLoginError(f"获取微信用户信息失败: {result.get('errmsg', '未知错误')}")
            
            return result
        except Exception as e:
            logger.exception(f"获取微信用户信息异常: {str(e)}")
            raise WechatLoginError(f"获取微信用户信息异常: {str(e)}")
    
    def validate_state(self, state):
        """
        验证状态码
        
        Args:
            state: 状态码
            
        Returns:
            state_obj: 状态对象
        """
        try:
            state_obj = WechatLoginState.objects.get(state=state, is_used=False)
            
            # 检查是否过期
            if state_obj.is_expired:
                raise WechatLoginError("微信登录状态已过期，请重新登录")
            
            # 标记为已使用
            state_obj.is_used = True
            state_obj.save(update_fields=['is_used'])
            
            return state_obj
        except WechatLoginState.DoesNotExist:
            raise WechatLoginError("无效的微信登录状态，请重新登录")
        except Exception as e:
            logger.exception(f"验证微信登录状态异常: {str(e)}")
            raise WechatLoginError(f"验证微信登录状态异常: {str(e)}")

# 创建微信登录工具类实例
wechat_login = WechatLogin()

class WechatMiniLogin:
    """微信小程序登录工具类"""
    
    # 获取小程序授权访问令牌API地址
    ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/sns/jscode2session'
    
    def __init__(self):
        """初始化微信小程序登录工具类"""
        # 使用与微信网页登录相同的配置参数
        self.app_id = getattr(settings, 'WECHAT_APP_ID', '')
        self.app_secret = getattr(settings, 'WECHAT_APP_SECRET', '')
        
        # 添加调试信息
        print(f"读取到的微信小程序配置 - app_id: '{self.app_id}', app_secret长度: {len(self.app_secret) if self.app_secret else 0}")
        
        if not self.app_id or not self.app_secret:
            logger.warning("微信登录配置缺失，请在settings.py中设置WECHAT_APP_ID和WECHAT_APP_SECRET")
    
    def get_session_info(self, code):
        """
        获取微信小程序会话信息
        
        Args:
            code: 临时登录凭证
            
        Returns:
            openid: 用户唯一标识
            session_key: 会话密钥
            unionid: 用户在开放平台的唯一标识符（如果有）
        """
        params = {
            'appid': self.app_id,
            'secret': self.app_secret,
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        
        # 添加调试信息
        print(f"微信小程序请求参数: {params}")
        
        try:
            response = requests.get(self.ACCESS_TOKEN_URL, params=params)
            result = response.json()
            
            if 'errcode' in result and result['errcode'] != 0:
                logger.error(f"获取微信小程序会话信息失败: {result}")
                raise WechatLoginError(f"获取微信小程序会话信息失败: {result.get('errmsg', '未知错误')}")
            
            return result
        except Exception as e:
            logger.exception(f"获取微信小程序会话信息异常: {str(e)}")
            raise WechatLoginError(f"获取微信小程序会话信息异常: {str(e)}")

# 创建微信小程序登录工具类实例
wechat_mini_login = WechatMiniLogin()

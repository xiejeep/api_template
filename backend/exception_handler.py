from rest_framework.views import exception_handler
from rest_framework import exceptions, status
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from .utils import api_error_response

def custom_exception_handler(exc, context):
    """
    自定义异常处理器
    
    Args:
        exc: 异常对象
        context: 上下文
        
    Returns:
        Response: 自定义API响应
    """
    # 首先调用REST framework的默认异常处理器
    response = exception_handler(exc, context)
    
    # 如果异常已经被处理
    if response is not None:
        # 获取错误详情
        if hasattr(exc, 'detail'):
            error_message = str(exc.detail)
        else:
            error_message = str(exc)
        
        # 根据异常类型设置错误码和状态码
        if isinstance(exc, exceptions.AuthenticationFailed):
            code = 1001
            message = f"认证失败: {error_message}"
        elif isinstance(exc, exceptions.NotAuthenticated):
            code = 1002
            message = "未认证"
        elif isinstance(exc, exceptions.PermissionDenied):
            code = 1003
            message = f"权限不足: {error_message}"
        elif isinstance(exc, exceptions.NotFound):
            code = 1004
            message = f"资源不存在: {error_message}"
        elif isinstance(exc, exceptions.MethodNotAllowed):
            code = 1005
            message = f"方法不允许: {error_message}"
        elif isinstance(exc, exceptions.ValidationError):
            code = 1006
            message = f"验证错误: {error_message}"
        elif isinstance(exc, exceptions.Throttled):
            code = 1007
            message = f"请求频率超限: {error_message}"
        else:
            code = 1000
            message = f"未知错误: {error_message}"
        
        # 返回自定义响应
        return api_error_response(
            code=code,
            message=message,
            status=response.status_code
        )
    
    # 处理其他异常
    if isinstance(exc, Http404):
        return api_error_response(
            code=1004,
            message=f"资源不存在: {str(exc)}",
            status=status.HTTP_404_NOT_FOUND
        )
    elif isinstance(exc, PermissionDenied):
        return api_error_response(
            code=1003,
            message=f"权限不足: {str(exc)}",
            status=status.HTTP_403_FORBIDDEN
        )
    elif isinstance(exc, IntegrityError):
        return api_error_response(
            code=1008,
            message=f"数据完整性错误: {str(exc)}",
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 处理未捕获的异常
    return api_error_response(
        code=9999,
        message=f"服务器错误: {str(exc)}",
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

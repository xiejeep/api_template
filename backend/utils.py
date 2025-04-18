from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from django.db.models import QuerySet
from collections import OrderedDict

class APIResponse(Response):
    """
    自定义API响应类
    
    统一API返回格式：
    {
        "code": 0,           # 错误码，0表示成功，非0表示错误
        "message": "成功",    # 错误消息或成功提示
        "data": { ... },     # 实际数据，可以是对象、数组或null
        "pagination": {      # 分页信息，如果不是分页请求则为null
            "page": 1,       # 当前页码
            "page_size": 10, # 每页数量
            "total_pages": 5,# 总页数
            "total_items": 42# 总条数
        }
    }
    """
    
    def __init__(self, data=None, code=0, message="成功", 
                 pagination=None, status=status.HTTP_200_OK, 
                 template_name=None, headers=None,
                 exception=False, content_type=None):
        """
        初始化API响应
        
        Args:
            data: 响应数据
            code: 错误码，0表示成功，非0表示错误
            message: 错误消息或成功提示
            pagination: 分页信息
            status: HTTP状态码
            template_name: 模板名称
            headers: HTTP头
            exception: 是否为异常响应
            content_type: 内容类型
        """
        response_data = {
            "code": code,
            "message": message,
            "data": data,
            "pagination": pagination
        }
        
        super().__init__(
            data=response_data,
            status=status,
            template_name=template_name,
            headers=headers,
            exception=exception,
            content_type=content_type
        )

def api_success_response(data=None, message="成功", pagination=None, status=status.HTTP_200_OK, **kwargs):
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 成功提示
        pagination: 分页信息
        status: HTTP状态码
        **kwargs: 其他参数
        
    Returns:
        APIResponse: 自定义API响应
    """
    return APIResponse(
        data=data,
        code=0,
        message=message,
        pagination=pagination,
        status=status,
        **kwargs
    )

def api_error_response(code=1, message="失败", status=status.HTTP_400_BAD_REQUEST, **kwargs):
    """
    错误响应
    
    Args:
        code: 错误码，非0表示错误
        message: 错误消息
        status: HTTP状态码
        **kwargs: 其他参数
        
    Returns:
        APIResponse: 自定义API响应
    """
    return APIResponse(
        data=None,
        code=code,
        message=message,
        pagination=None,
        status=status,
        **kwargs
    )

def paginate_queryset(queryset, request, page_size=10):
    """
    分页查询集
    
    Args:
        queryset: 查询集
        request: 请求对象
        page_size: 每页数量
        
    Returns:
        tuple: (分页数据, 分页信息)
    """
    # 获取页码参数，默认为1
    page = request.query_params.get('page', 1)
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1
    
    # 获取每页数量参数，默认为page_size
    size = request.query_params.get('page_size', page_size)
    try:
        size = int(size)
    except (TypeError, ValueError):
        size = page_size
    
    # 限制每页数量
    if size > 100:
        size = 100
    
    # 创建分页器
    paginator = Paginator(queryset, size)
    
    # 获取当前页的数据
    try:
        page_obj = paginator.page(page)
    except:
        # 如果页码超出范围，返回最后一页
        page_obj = paginator.page(paginator.num_pages)
    
    # 构建分页信息
    pagination = {
        "page": page_obj.number,
        "page_size": size,
        "total_pages": paginator.num_pages,
        "total_items": paginator.count
    }
    
    return page_obj.object_list, pagination

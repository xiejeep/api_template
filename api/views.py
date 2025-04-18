from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from backend.utils import api_success_response, api_error_response, paginate_queryset
from .models import Task
from .serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    """
    任务管理API
    ---
    list:
        描述: 获取任务列表
        参数:
            - name: page
              description: 页码，默认为1
              required: false
              type: integer
              example: 1
            - name: page_size
              description: 每页数量，默认为10
              required: false
              type: integer
              example: 10
        响应:
            200:
                描述: 获取任务列表成功
                示例:
                    {
                        "code": 0,
                        "message": "获取任务列表成功",
                        "data": {
                            "tasks": [
                                {
                                    "id": 1,
                                    "title": "测试任务",
                                    "description": "这是一个测试任务",
                                    "status": "pending",
                                    "created_at": "2025-04-18T12:00:00Z",
                                    "updated_at": "2025-04-18T12:00:00Z"
                                }
                            ]
                        },
                        "pagination": {
                            "page": 1,
                            "page_size": 10,
                            "total_pages": 1,
                            "total_items": 1
                        }
                    }

    create:
        描述: 创建新任务
        参数:
            - name: title
              description: 任务标题
              required: true
              type: string
              example: "新任务"
            - name: description
              description: 任务描述
              required: false
              type: string
              example: "这是一个新任务"
            - name: status
              description: 任务状态，可选值：pending(待处理), in_progress(进行中), completed(已完成), cancelled(已取消)
              required: false
              type: string
              example: "pending"
        响应:
            201:
                描述: 创建任务成功
                示例:
                    {
                        "code": 0,
                        "message": "创建任务成功",
                        "data": {
                            "task": {
                                "id": 2,
                                "title": "新任务",
                                "description": "这是一个新任务",
                                "status": "pending",
                                "created_at": "2025-04-18T13:00:00Z",
                                "updated_at": "2025-04-18T13:00:00Z"
                            }
                        },
                        "pagination": null
                    }
            400:
                描述: 创建任务失败
                示例:
                    {
                        "code": 1006,
                        "message": "创建任务失败",
                        "data": null,
                        "pagination": null
                    }

    retrieve:
        描述: 获取任务详情
        参数:
            - name: id
              description: 任务ID
              required: true
              type: integer
              example: 1
        响应:
            200:
                描述: 获取任务详情成功
                示例:
                    {
                        "code": 0,
                        "message": "获取任务详情成功",
                        "data": {
                            "task": {
                                "id": 1,
                                "title": "测试任务",
                                "description": "这是一个测试任务",
                                "status": "pending",
                                "created_at": "2025-04-18T12:00:00Z",
                                "updated_at": "2025-04-18T12:00:00Z"
                            }
                        },
                        "pagination": null
                    }
            404:
                描述: 任务不存在
                示例:
                    {
                        "code": 1004,
                        "message": "资源不存在",
                        "data": null,
                        "pagination": null
                    }

    update:
        描述: 更新任务
        参数:
            - name: id
              description: 任务ID
              required: true
              type: integer
              example: 1
            - name: title
              description: 任务标题
              required: true
              type: string
              example: "更新后的任务"
            - name: description
              description: 任务描述
              required: true
              type: string
              example: "这是一个更新后的任务"
            - name: status
              description: 任务状态
              required: true
              type: string
              example: "completed"
        响应:
            200:
                描述: 更新任务成功
                示例:
                    {
                        "code": 0,
                        "message": "更新任务成功",
                        "data": {
                            "task": {
                                "id": 1,
                                "title": "更新后的任务",
                                "description": "这是一个更新后的任务",
                                "status": "completed",
                                "created_at": "2025-04-18T12:00:00Z",
                                "updated_at": "2025-04-18T13:30:00Z"
                            }
                        },
                        "pagination": null
                    }
            400:
                描述: 更新任务失败
                示例:
                    {
                        "code": 1006,
                        "message": "更新任务失败",
                        "data": null,
                        "pagination": null
                    }
            404:
                描述: 任务不存在
                示例:
                    {
                        "code": 1004,
                        "message": "资源不存在",
                        "data": null,
                        "pagination": null
                    }

    partial_update:
        描述: 部分更新任务
        参数:
            - name: id
              description: 任务ID
              required: true
              type: integer
              example: 1
            - name: status
              description: 任务状态
              required: false
              type: string
              example: "in_progress"
        响应:
            200:
                描述: 部分更新任务成功
                示例:
                    {
                        "code": 0,
                        "message": "更新任务成功",
                        "data": {
                            "task": {
                                "id": 1,
                                "title": "测试任务",
                                "description": "这是一个测试任务",
                                "status": "in_progress",
                                "created_at": "2025-04-18T12:00:00Z",
                                "updated_at": "2025-04-18T13:30:00Z"
                            }
                        },
                        "pagination": null
                    }
            400:
                描述: 部分更新任务失败
                示例:
                    {
                        "code": 1006,
                        "message": "更新任务失败",
                        "data": null,
                        "pagination": null
                    }
            404:
                描述: 任务不存在
                示例:
                    {
                        "code": 1004,
                        "message": "资源不存在",
                        "data": null,
                        "pagination": null
                    }

    destroy:
        描述: 删除任务
        参数:
            - name: id
              description: 任务ID
              required: true
              type: integer
              example: 1
        响应:
            204:
                描述: 删除任务成功
                示例:
                    {
                        "code": 0,
                        "message": "删除任务成功",
                        "data": null,
                        "pagination": null
                    }
            404:
                描述: 任务不存在
                示例:
                    {
                        "code": 1004,
                        "message": "资源不存在",
                        "data": null,
                        "pagination": null
                    }
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """允许未登录用户查看和创建任务"""
        if self.action in ['list', 'retrieve', 'create']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        """获取任务列表"""
        queryset = self.filter_queryset(self.get_queryset())

        # 分页
        page_data, pagination = paginate_queryset(queryset, request)

        serializer = self.get_serializer(page_data, many=True)
        return api_success_response(
            data={'tasks': serializer.data},
            message='获取任务列表成功',
            pagination=pagination
        )

    def retrieve(self, request, *args, **kwargs):
        """获取任务详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_success_response(
            data={'task': serializer.data},
            message='获取任务详情成功'
        )

    def create(self, request, *args, **kwargs):
        """创建任务"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return api_success_response(
                data={'task': serializer.data},
                message='创建任务成功',
                status=status.HTTP_201_CREATED
            )
        return api_error_response(
            code=1006,
            message='创建任务失败',
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        """更新任务"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return api_success_response(
                data={'task': serializer.data},
                message='更新任务成功'
            )
        return api_error_response(
            code=1006,
            message='更新任务失败',
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        """删除任务"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return api_success_response(
            data=None,
            message='删除任务成功',
            status=status.HTTP_204_NO_CONTENT
        )

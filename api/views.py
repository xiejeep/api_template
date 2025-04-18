from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from backend.utils import api_success_response, api_error_response, paginate_queryset
from .models import Task
from .serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    """
    任务管理API

    list:
        获取任务列表

    create:
        创建新任务

    retrieve:
        获取任务详情

    update:
        更新任务

    partial_update:
        部分更新任务

    destroy:
        删除任务
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

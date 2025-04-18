from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet

# 创建路由器
router = DefaultRouter()
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # 添加DRF的登录URL
    path('auth/', include('rest_framework.urls')),
]

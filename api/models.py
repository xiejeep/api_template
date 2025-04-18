from django.db import models
from django.utils import timezone

# Create your models here.

class Task(models.Model):
    """
    任务模型

    字段说明:
        - title: 任务标题，最大长度200个字符
        - description: 任务描述，可以为空
        - status: 任务状态，可选值包括：
            - pending: 待处理
            - in_progress: 进行中
            - completed: 已完成
            - cancelled: 已取消
        - created_at: 创建时间，自动设置为当前时间
        - updated_at: 更新时间，自动更新
    """
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )

    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '任务'
        verbose_name_plural = '任务'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

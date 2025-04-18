# Generated by Django 5.2 on 2025-04-18 12:26

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='标题')),
                ('description', models.TextField(blank=True, null=True, verbose_name='描述')),
                ('status', models.CharField(choices=[('pending', '待处理'), ('in_progress', '进行中'), ('completed', '已完成'), ('cancelled', '已取消')], default='pending', max_length=20, verbose_name='状态')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '任务',
                'verbose_name_plural': '任务',
                'ordering': ['-created_at'],
            },
        ),
    ]

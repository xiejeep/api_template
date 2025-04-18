from django.contrib import admin
from .models import Task

# Register your models here.
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, VerificationCode

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'phone', 'email', 'is_phone_verified', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_phone_verified')
    search_fields = ('username', 'phone', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('个人信息'), {'fields': ('phone', 'email', 'is_phone_verified')}),
        (_('权限信息'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('重要日期'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone', 'password1', 'password2'),
        }),
    )

@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('phone', 'code', 'purpose', 'created_at', 'expires_at', 'is_used', 'is_expired')
    list_filter = ('purpose', 'is_used')
    search_fields = ('phone',)
    readonly_fields = ('is_expired',)

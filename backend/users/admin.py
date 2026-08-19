from django.contrib import admin
from .models import CustomUser, UserProfile
from django.contrib.auth.admin import UserAdmin


class InlineUserProfileAdmin(admin.StackedInline):
    model = UserProfile


class CustomUserAdmin(UserAdmin):
    inlines = [InlineUserProfileAdmin]
    fieldsets = UserAdmin.fieldsets + (
        ('SAML', {
            'fields': ('saml', 'saml_username')
        }),
        ('Extra fields', {
            'fields': ('download_limit',)
        }),
    )
    readonly_fields = ['saml', 'saml_username']
    list_display = [
        '__str__', 'email', 'is_staff', 'saml',
    ]
    list_filter = list(UserAdmin.list_filter) + ['saml']
    search_fields = list(UserAdmin.search_fields) + ['saml_username']


admin.site.register(CustomUser, CustomUserAdmin)

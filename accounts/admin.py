from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin



class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'date_of_birth', 'is_admin', 'is_staff')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'date_of_birth', 'role', 'is_active', 'is_staff')}),
        ('Permissions', {'fields': ('is_admin', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'date_of_birth', 'password1', 'password2', 'role', 'is_active', 'is_staff'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


class MagistrateParentAdmin(admin.ModelAdmin):
    list_display = ('magistrate', 'parent')
    search_fields = ('magistrate__email', 'parent__email')


admin.site.register(User, UserAdmin)
# admin.site.register(MagistrateParent, MagistrateParentAdmin)

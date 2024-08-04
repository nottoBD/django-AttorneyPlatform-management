"""
Neok-Budget: A Django-based web application for budgeting.
Copyright (C) 2024  David Botton, Arnaud Mahieu

Developed for Jurinet and its branch Neok-Budget.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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

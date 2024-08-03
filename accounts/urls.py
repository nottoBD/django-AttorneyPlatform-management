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

from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetDoneView, PasswordResetCompleteView
from django.urls import path, reverse_lazy
from django.conf import settings

from . import views
from .views import register_jurist, ResetPasswordView, PasswordResetConfirmationView, delete_user

app_name = 'accounts'
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('accounts:login')), name='logout'),
    path('register/', views.register, name='register'),
    path('register-jurist/', views.register_jurist, name='register_jurist'),
    path('update/<uuid:pk>/', views.UserUpdateView.as_view(), name='user_update'),
    path('list/', views.UserListView.as_view(), name='user_list'),
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmationView.as_view(), name='password_reset_confirmation'),
    path('password-reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('request_deletion/<uuid:pk>/', views.request_deletion, name='request_deletion'),
    path('cancel_deletion/<uuid:pk>/', views.cancel_deletion, name='cancel_deletion'),
    path('delete/<uuid:pk>/', delete_user, name='delete_user'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

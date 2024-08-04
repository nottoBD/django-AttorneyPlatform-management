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

import django.core.validators
import django.utils.timezone
import uuid
from django.db import migrations, models

import accounts.validations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='JugeCase',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('username', models.CharField(blank=True, max_length=150, null=True)),
                ('email', models.EmailField(max_length=255, unique=True, validators=[django.core.validators.EmailValidator()], verbose_name='e-mail address')),
                ('is_active', models.BooleanField(default=True)),
                ('deletion_requested_at', models.DateTimeField(blank=True, null=True)),
                ('role', models.CharField(choices=[('administrator', 'Administrator'), ('lawyer', 'Attorney'), ('judge', 'Judge'), ('parent', 'Parent')], default='parent', max_length=13)),
                ('is_staff', models.BooleanField(default=False)),
                ('last_name', models.CharField(blank=True, max_length=35, verbose_name='last name')),
                ('first_name', models.CharField(blank=True, max_length=25, verbose_name='first name')),
                ('date_of_birth', models.DateField(default=django.utils.timezone.now)),
                ('telephone', models.CharField(blank=True, max_length=16, null=True, validators=[accounts.validations.validate_telephone])),
                ('address', models.CharField(blank=True, max_length=75, null=True)),
                ('national_number', models.CharField(blank=True, max_length=11, null=True, unique=True, validators=[accounts.validations.validate_national_number])),
                ('profile_image', models.ImageField(default='profile_images/default.png', upload_to='profile_images/', validators=[accounts.validations.validate_image])),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AvocatCase',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
        ),
    ]

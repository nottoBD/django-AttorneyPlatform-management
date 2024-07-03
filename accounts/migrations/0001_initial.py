# Generated by Django 5.0.3 on 2024-07-02 20:32

import accounts.validations
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(blank=True, max_length=150, null=True)),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='e-mail address')),
                ('is_active', models.BooleanField(default=True)),
                ('deletion_requested_at', models.DateTimeField(blank=True, null=True)),
                ('role', models.CharField(choices=[('administrator', 'Administrator'), ('magistrate', 'Magistrate'), ('lawyer', 'Lawyer'), ('judge', 'Judge'), ('parent', 'Parent')], default='parent', max_length=13)),
                ('is_staff', models.BooleanField(default=False)),
                ('gender', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('X', 'They')], default=' ', max_length=1, null=True)),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('date_of_birth', models.DateField(default=django.utils.timezone.now)),
                ('telephone', models.CharField(blank=True, max_length=16, null=True)),
                ('address', models.CharField(blank=True, max_length=75, null=True)),
                ('national_number_raw', models.CharField(blank=True, max_length=11, null=True)),
                ('national_number', models.CharField(blank=True, max_length=15, null=True)),
                ('profile_image', models.ImageField(default='profile_images/default.jpg', upload_to='profile_images/', validators=[accounts.validations.validate_image])),
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
            name='MagistrateParent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('magistrate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parents_assigned', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='magistrates_assigned', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('magistrate', 'parent')},
            },
        ),
    ]

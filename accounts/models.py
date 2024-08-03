import uuid

from django.conf import settings
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractUser
from django.db import models
from django.utils import timezone
from guardian.shortcuts import assign_perm
from datetime import timedelta

from .validations import validate_image


# Permet un import différé pour éviter l'import circulaire et générer un message d'erreur
def get_case_model():
    from payments.models import Case
    return Case


class CustomUserManager(BaseUserManager):
    def create_user(self, email, role="parent", password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        if role == 'parent':
            assign_perm('accounts.view_user', user, user)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('role', 'administrator')
        return self.create_user(email, password=password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('administrator', 'Administrator'),
        ('lawyer', 'Attorney'),
        ('judge', 'Judge'),
        ('parent', 'Parent'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=False, null=True, blank=True)
    email = models.EmailField(verbose_name='e-mail address', unique=True, max_length=255)
    is_active = models.BooleanField(default=True)
    deletion_requested_at = models.DateTimeField(null=True, blank=True)
    role = models.CharField(max_length=13, choices=ROLE_CHOICES, default='parent')
    is_staff = models.BooleanField(default=False)
    last_name = models.CharField('last name', max_length=35, blank=True)
    first_name = models.CharField('first name', max_length=25, blank=True)
    date_of_birth = models.DateField(default=timezone.now)
    telephone = models.CharField(max_length=16, null=True, blank=True)
    address = models.CharField(null=True, blank=True, max_length=75)
    national_number = models.CharField(max_length=11, blank=True, null=True, unique=True)
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/default.png',
                                      validators=[validate_image])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.last_name}"

    @property
    def is_administrator(self):
        return self.role == 'administrator'

    def is_lawyer(self):
        return self.role == 'lawyer'

    def is_judge(self):
        return self.role == 'judge'

    @property
    def is_parent(self):
        return self.role == 'parent'

    def request_deletion(self):
        self.deletion_requested_at = timezone.now()
        self.save()

    def cancel_deletion(self):
        self.deletion_requested_at = None
        self.save()

    def is_deletion_pending(self):
        return self.deletion_requested_at and (timezone.now() < self.deletion_requested_at + timedelta(days=30))

    def get_formatted_national_number(self):
        nn = self.national_number_raw
        if nn and len(nn) == 11:
            return f"{nn[:2]}.{nn[2:4]}.{nn[4:6]}-{nn[6:9]}.{nn[9:]}"
        return nn


class AvocatCase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avocat = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_parents', on_delete=models.CASCADE)
    case = models.ForeignKey(get_case_model(), on_delete=models.CASCADE, related_name='assigned_lawyers')

    class Meta:
        unique_together = (('avocat', 'case'),)

    def __str__(self):
        return f"{self.avocat.email}"


class JugeCase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    juge = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_parents_judge', on_delete=models.CASCADE)
    case = models.ForeignKey(get_case_model(), on_delete=models.CASCADE, related_name='assigned_judges')

    class Meta:
        unique_together = (('juge', 'case'),)

    def __str__(self):
        return f"{self.juge.email} assigned to case {self.case.id}"

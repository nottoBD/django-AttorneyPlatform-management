import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class CategoryType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    type = models.ForeignKey(CategoryType, on_delete=models.CASCADE, related_name='payment_categories')

    def __str__(self):
        return self.name


class Document(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),  # En attente de validation
        ('validated', 'Validated'),  # Validé par l'avocat
        ('rejected', 'Rejected'),  # Rejeté par l'avocat
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE, related_name='payment_documents', blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='payments', blank=False)
    document = models.FileField(upload_to='payment_documents/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Payment Document - {self.user.username} - {self.date} - {self.amount}"

    def user_can_delete(self, user):
        return self.user == user

    def is_validated(self):
        return self.status == 'validated'


class Folder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='folders_as_parent1')
    parent2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='folders_as_parent2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Folder managed by {self.lawyer} with parents {self.parent1} and {self.parent2}"


class IndexHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Indexation {self.percentage}% for {self.year}"
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import ListView

from accounts.models import User

from .validations import validate_image


class PaymentDocument(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE, related_name='payment_documents', blank=True,
                               null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    document = models.FileField(upload_to='payment_documents/', blank=True, null=True)

    def __str__(self):
        return f"Payment Document - {self.user.username} - {self.date} - {self.amount}"

    def user_can_delete(self, user):
        return self.user == user


class Folder(models.Model):
    lawyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='folders_in_charge')
    magistrate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='folders_visible', null=True, blank=True)
    parent1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='folders_as_parent1')
    parent2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='folders_as_parent2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Folder managed by {self.lawyer} with parents {self.parent1} and {self.parent2}"
from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from payments.models import Child, Case

User = get_user_model()

class ChildViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            email='superuser@example.com',
            password='ComplexPassword1!'
        )
        self.client.login(email='superuser@example.com', password='ComplexPassword1!')

        self.parent1 = User.objects.create_user(email='parent1@example.com', password='ComplexPassword1!', role='parent')
        self.parent2 = User.objects.create_user(email='parent2@example.com', password='ComplexPassword1!', role='parent')

        self.case = Case.objects.create(parent1=self.parent1, parent2=self.parent2, created_at=timezone.now(), updated_at=timezone.now())

    def test_child_list_view(self):
        response = self.client.get(reverse('payments:child', kwargs={'case_id': self.case.id}))
        self.assertEqual(response.status_code, 200)

    def test_child_detail_view(self):
        child = Child.objects.create(case=self.case, first_name='Jean', last_name='Dupont', birth_date='2010-05-15')
        response = self.client.get(reverse('payments:child', kwargs={'case_id': self.case.id}))
        self.assertEqual(response.status_code, 200)

    def test_child_create_view(self):
        response = self.client.get(reverse('payments:child', kwargs={'case_id': self.case.id}))
        self.assertEqual(response.status_code, 200)
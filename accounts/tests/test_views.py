from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import User

User = get_user_model()

class UserUpdateViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='ComplexPassword1!',
            role='administrator',
            is_superuser=True
        )
        self.target_user = User.objects.create_user(
            email='target@example.com',
            first_name='Target',
            last_name='User',
            password='ComplexPassword1!',
            role='parent'
        )
        self.client.login(email='admin@example.com', password='ComplexPassword1!')
        self.url = reverse('accounts:user_update', args=[self.target_user.pk])

    def test_get_user_update_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_update.html')

    def test_post_user_update_view(self):
        data = {
            'first_name': 'UpdatedFirstName',
            'last_name': 'UpdatedLastName',
            'email': 'updated@example.com',
            'is_active': True
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.first_name, 'UpdatedFirstName')
        self.assertEqual(self.target_user.last_name, 'UpdatedLastName')
        self.assertEqual(self.target_user.email, 'updated@example.com')


class UserListViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='ComplexPassword1!',
            role='administrator',
            is_superuser=True,
            is_staff=True
        )
        self.client.login(email='admin@example.com', password='ComplexPassword1!')
        self.url = reverse('accounts:user_list')

    def test_get_user_list_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_list.html')


class RegisterJuristViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            email='superuser@example.com',
            password='ComplexPassword1!'
        )
        self.client.login(email='superuser@example.com', password='ComplexPassword1!')
        self.url = reverse('accounts:register_jurist')

    def test_get_register_jurist_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register_jurist.html')

    def test_post_register_jurist_view(self):
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'jurist@example.com',
            'password1': 'ComplexPassword1!',
            'password2': 'ComplexPassword1!',
            'role': 'judge'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='jurist@example.com').exists())


class RegisterViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('accounts:register')

    def test_get_register_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_post_register_view(self):
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'parent@example.com',
            'password1': 'ComplexPassword1!',
            'password2': 'ComplexPassword1!',
            'national_number': '12.03.05-789.01',
            'date_of_birth': '2000-01-01',
            'address': '123 Main St',
            'telephone': '+32123456789'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='parent@example.com').exists())


class RequestDeletionViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='user@example.com',
            first_name='User',
            last_name='Example',
            password='ComplexPassword1!',
            role='parent'
        )
        self.client.login(email='user@example.com', password='ComplexPassword1!')
        self.url = reverse('accounts:request_deletion', args=[self.user.pk])

    def test_get_request_deletion_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/request_deletion.html')

    def test_post_request_deletion_view(self):
        response = self.client.post(self.url, {'confirm': True})
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.deletion_requested_at is not None)


class CancelDeletionViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='user@example.com',
            first_name='User',
            last_name='Example',
            password='ComplexPassword1!',
            role='parent'
        )
        self.user.request_deletion()
        self.client.login(email='user@example.com', password='ComplexPassword1!')
        self.url = reverse('accounts:cancel_deletion', args=[self.user.pk])

    def test_get_cancel_deletion_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/cancel_deletion.html')

    def test_post_cancel_deletion_view(self):
        response = self.client.post(self.url, {'confirm': True})
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.deletion_requested_at is None)


class DeleteUserViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            email='superuser@example.com',
            password='ComplexPassword1!'
        )
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='ComplexPassword1!',
            role='administrator',
            is_superuser=True
        )
        self.target_user = User.objects.create_user(
            email='target@example.com',
            first_name='Target',
            last_name='User',
            password='ComplexPassword1!',
            role='parent'
        )
        self.client.login(email='admin@example.com', password='ComplexPassword1!')
        self.url = reverse('accounts:delete_user', args=[self.target_user.pk])

    def test_delete_user_view(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(email='target@example.com').exists())

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

        self.case = Case.objects.create(name='Test Case')
        self.child = Child.objects.create(
            case=self.case,
            first_name='Jean',
            last_name='Dupont',
            birth_date='2010-05-15'
        )

    def test_child_list_view(self):
        url = reverse('child_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'your_app/child_list.html')
        self.assertContains(response, 'Jean Dupont')

    def test_child_detail_view(self):
        url = reverse('child_detail', args=[self.child.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'your_app/child_detail.html')
        self.assertContains(response, 'Jean Dupont')

    def test_child_create_view(self):
        url = reverse('child_create')
        data = {
            'first_name': 'Marie',
            'last_name': 'Curie',
            'birth_date': '2012-08-12',
            'case': self.case.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertTrue(Child.objects.filter(first_name='Marie', last_name='Curie').exists())

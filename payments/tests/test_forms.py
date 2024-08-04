from django.test import TestCase
from django.utils import timezone
from accounts.models import User
from payments.models import Case, Child
from payments.forms import ChildForm
from datetime import date

class ChildFormTest(TestCase):
    def setUp(self):
        self.parent1 = User.objects.create_user(email='parent1@example.com', password='Complexpassword1!', role='parent')
        self.parent2 = User.objects.create_user(email='parent2@example.com', password='Complexpassword1!', role='parent')
        self.case = Case.objects.create(parent1=self.parent1, parent2=self.parent2, created_at=timezone.now(), updated_at=timezone.now())

    def test_valid_form(self):
        form_data = {
            'first_name': 'Jean-Pierre',
            'last_name': 'Dupont',
            'birth_date': '2010-05-15',
            'case': self.case.id
        }
        form = ChildForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_first_name(self):
        form_data = {
            'first_name': 'Jean123',
            'last_name': 'Dupont',
            'birth_date': '2010-05-15',
            'case': self.case.id
        }
        form = ChildForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_invalid_last_name(self):
        form_data = {
            'first_name': 'Jean',
            'last_name': 'Dupont!',
            'birth_date': '2010-05-15',
            'case': self.case.id
        }
        form = ChildForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors)

    def test_future_birth_date(self):
        form_data = {
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'birth_date': (date.today().replace(year=date.today().year + 1)).isoformat(),
            'case': self.case.id
        }
        form = ChildForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('birth_date', form.errors)

    def test_empty_form(self):
        form_data = {}
        form = ChildForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)
        self.assertIn('birth_date', form.errors)
        self.assertIn('case', form.errors)

from django.test import TestCase
from django.core.exceptions import ValidationError
from payments.forms import (ChildForm)
from datetime import date
from payments.models import Child, Case


class ChildFormTest(TestCase):
    def setUp(self):
        self.case = Case.objects.create(name='Test Case')

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

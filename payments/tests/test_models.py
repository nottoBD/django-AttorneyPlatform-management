from django.test import TestCase
from payments.models import Child, Case
from datetime import date
import uuid

class ChildModelTest(TestCase):
    def setUp(self):
        self.case = Case.objects.create(name='Test Case')
        self.child = Child.objects.create(
            case=self.case,
            first_name='Jean',
            last_name='Dupont',
            birth_date='2010-05-15'
        )

    def test_child_creation(self):
        self.assertEqual(self.child.first_name, 'Jean')
        self.assertEqual(self.child.last_name, 'Dupont')
        self.assertEqual(self.child.birth_date, date(2010, 5, 15))
        self.assertEqual(self.child.case, self.case)
        self.assertIsInstance(self.child.id, uuid.UUID)

    def test_str_representation(self):
        self.assertEqual(str(self.child), 'Jean Dupont')

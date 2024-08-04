from django.test import TestCase
from payments.models import Child, Case
from django.utils import timezone
from datetime import date
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

class ChildModelTest(TestCase):
    def setUp(self):
        self.parent1 = User.objects.create_user(email='parent1@example.com', password='ComplexPassword1!', role='parent')
        self.parent2 = User.objects.create_user(email='parent2@example.com', password='ComplexPassword1!', role='parent')

        self.case = Case.objects.create(
            parent1=self.parent1,
            parent2=self.parent2,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        self.child = Child.objects.create(
            case=self.case,
            first_name='Jean',
            last_name='Dupont',
            birth_date=date(2010, 5, 15)
        )

    def test_child_creation(self):
        self.assertEqual(self.child.first_name, 'Jean')
        self.assertEqual(self.child.last_name, 'Dupont')
        self.assertEqual(self.child.birth_date, date(2010, 5, 15))
        self.assertEqual(self.child.case, self.case)
        self.assertIsInstance(self.child.id, uuid.UUID)

    def test_str_representation(self):
        self.assertEqual(str(self.child), 'Jean Dupont')

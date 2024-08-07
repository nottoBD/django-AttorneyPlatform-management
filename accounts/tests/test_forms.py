from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.forms import UserUpdateForm, JusticeRegistrationForm, UserRegisterForm, DeletionRequestForm, CancelDeletionForm
from accounts.models import User
from payments.models import Case
from PIL import Image
import tempfile

class UserUpdateFormTestCase(TestCase):

    def setUp(self):
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
            password='ComplexPassword1!'
        )
        self.case = Case.objects.create(
            parent1=self.target_user,
            parent2=None,
            draft=False
        )

    def test_clean_email(self):
        form = UserUpdateForm(data={
            'email': 'new@example.com',
            'first_name': 'Target',
            'last_name': 'User',
            'is_active': True
        }, instance=self.target_user, request_user=self.admin_user)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['email'], 'new@example.com')

    def test_clean_first_name(self):
        form = UserUpdateForm(data={
            'first_name': 'NewFirstName',
            'last_name': 'User',
            'email': 'target@example.com',
            'is_active': True
        }, instance=self.target_user, request_user=self.admin_user)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['first_name'], 'NewFirstName')

    def test_clean_last_name(self):
        form = UserUpdateForm(data={
            'last_name': 'NewLastName',
            'first_name': 'Target',
            'email': 'target@example.com',
            'is_active': True
        }, instance=self.target_user, request_user=self.admin_user)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['last_name'], 'NewLastName')

    def test_clean_profile_image(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_file:
            image = Image.new('RGB', (100, 100))
            image.save(temp_file, format='JPEG')
            temp_file.seek(0)
            file = SimpleUploadedFile(temp_file.name, temp_file.read(), content_type='image/jpeg')

            form = UserUpdateForm(data={
                'first_name': 'Target',
                'last_name': 'User',
                'email': 'target@example.com',
                'is_active': True
            }, files={'profile_image': file}, instance=self.target_user, request_user=self.admin_user)
            self.assertTrue(form.is_valid(), form.errors)

    def test_clean_is_active_unauthorized(self):
        form = UserUpdateForm(data={
            'is_active': False,
            'first_name': 'Target',
            'last_name': 'User',
            'email': 'target@example.com'
        }, instance=self.target_user, request_user=self.target_user)
        self.assertFalse(form.is_valid())

    def test_clean_is_active_authorized(self):
        form = UserUpdateForm(data={
            'is_active': False,
            'first_name': 'Target',
            'last_name': 'User',
            'email': 'target@example.com'
        }, instance=self.target_user, request_user=self.admin_user)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertFalse(form.cleaned_data['is_active'])


class JusticeRegistrationFormTestCase(TestCase):

    def test_clean_first_name(self):
        form = JusticeRegistrationForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'judge@example.com',
            'password1': 'ComplexPassword1!',
            'password2': 'ComplexPassword1!',
            'role': 'judge'
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['first_name'], 'John')

    def test_clean_last_name(self):
        form = JusticeRegistrationForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'judge@example.com',
            'password1': 'ComplexPassword1!',
            'password2': 'ComplexPassword1!',
            'role': 'judge'
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['last_name'], 'Doe')

    def test_clean_email(self):
        form = JusticeRegistrationForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'judge@example.com',
            'password1': 'ComplexPassword1!',
            'password2': 'ComplexPassword1!',
            'role': 'judge'
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['email'], 'judge@example.com')

    def test_clean_password1(self):
        form = JusticeRegistrationForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'judge@example.com',
            'password1': 'ComplexPassword1!',
            'password2': 'ComplexPassword1!',
            'role': 'judge'
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['password1'], 'ComplexPassword1!')

    def test_save(self):
        form = JusticeRegistrationForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'judge@example.com',
            'password1': 'ComplexPassword1!',
            'password2': 'ComplexPassword1!',
            'role': 'judge'
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'judge@example.com')
        self.assertTrue(user.check_password('ComplexPassword1!'))
        self.assertEqual(user.role, 'judge')


class UserRegisterFormTestCase(TestCase):

    def test_clean_national_number(self):
        form = UserRegisterForm(data={
            'national_number': '12.03.05-789.01',
            'last_name': 'Doe',
            'first_name': 'John',
            'email': 'user@example.com',
            'date_of_birth': '2000-01-01',
            'address': '123 Main St',
            'telephone': '+32123456789',
            'password1': 'ComplexPassword1!',
            'password2': 'ComplexPassword1!'
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['national_number'], '12030578901')

    def test_clean_first_name(self):
        form = UserRegisterForm(data={
            'national_number': '12.03.05-789.01',
            'last_name': 'Doe',
            'first_name': 'John',
            'email': 'user@example.com',
            'date_of_birth': '2000-01-01',
            'address': '123 Main St',
            'telephone': '+32123456789',
            'password1': 'ComplexPassword1!',
            'password2': 'ComplexPassword1!'
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['first_name'], 'John')

    def test_clean_last_name(self):
        form = UserRegisterForm(data={
            'national_number': '12.03.05-789.01',
            'last_name': 'Doe',
            'first_name': 'John',
            'email': 'user@example.com',
            'date_of_birth': '2000-01-01',
            'address': '123 Main St',
            'telephone': '+32123456789',
            'password1': 'ComplexPassword1!',
            'password2': 'ComplexPassword1!'
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['last_name'], 'Doe')

    def test_clean_email(self):
        form = UserRegisterForm(data={
            'national_number': '12.03.05-789.01',
            'last_name': 'Doe',
            'first_name': 'John',
            'email': 'user@example.com',
            'date_of_birth': '2000-01-01',
            'address': '123 Main St',
            'telephone': '+32123456789',
            'password1': 'ComplexPassword1!',
            'password2': 'ComplexPassword1!'
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['email'], 'user@example.com')

    def test_clean_telephone(self):
        form = UserRegisterForm(data={
            'national_number': '12.03.05-789.01',
            'last_name': 'Doe',
            'first_name': 'John',
            'email': 'user@example.com',
            'date_of_birth': '2000-01-01',
            'address': '123 Main St',
            'telephone': '+32123456789',
            'password1': 'ComplexPassword1!',
            'password2': 'ComplexPassword1!'
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['telephone'], '+32123456789')

    def test_clean_password1(self):
        form = UserRegisterForm(data={
            'national_number': '12.03.05-789.01',
            'last_name': 'Doe',
            'first_name': 'John',
            'email': 'user@example.com',
            'date_of_birth': '2000-01-01',
            'address': '123 Main St',
            'telephone': '+32123456789',
            'password1': 'ComplexPassword1!',
            'password2': 'ComplexPassword1!'
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['password1'], 'ComplexPassword1!')

    def test_clean_password2(self):
        form = UserRegisterForm(data={
            'national_number': '12.03.05-789.01',
            'last_name': 'Doe',
            'first_name': 'John',
            'email': 'user@example.com',
            'date_of_birth': '2000-01-01',
            'address': '123 Main St',
            'telephone': '+32123456789',
            'password1': 'ComplexPassword1!',
            'password2': 'ComplexPassword1!'
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['password2'], 'ComplexPassword1!')


class DeletionRequestFormTestCase(TestCase):

    def test_form_valid(self):
        form = DeletionRequestForm(data={'confirm': True})
        self.assertTrue(form.is_valid(), form.errors)


class CancelDeletionFormTestCase(TestCase):

    def test_form_valid(self):
        form = CancelDeletionForm(data={'confirm': True})
        self.assertTrue(form.is_valid(), form.errors)

import tempfile

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from PIL import Image

from accounts.models import User, AvocatCase, JugeCase
from accounts.validations import validate_image, clean_email, sanitize_text, validate_national_number, validate_password, validate_telephone
from payments.models import Case
from django.utils import timezone
from datetime import timedelta
import uuid

class UserModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            first_name='Test',
            last_name='User',
            password='password123'
        )

    def test_create_user(self):
        user = User.objects.get(email='testuser@example.com')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertTrue(user.check_password('password123'))

    def test_is_administrator_property(self):
        self.assertFalse(self.user.is_administrator)
        self.user.role = 'administrator'
        self.user.save()
        self.assertTrue(self.user.is_administrator)

    def test_request_deletion(self):
        self.user.request_deletion()
        self.assertIsNotNone(self.user.deletion_requested_at)

    def test_cancel_deletion(self):
        self.user.request_deletion()
        self.user.cancel_deletion()
        self.assertIsNone(self.user.deletion_requested_at)

    def test_is_deletion_pending(self):
        self.user.request_deletion()
        self.assertTrue(self.user.is_deletion_pending())
        self.user.deletion_requested_at = timezone.now() - timedelta(days=31)
        self.user.save()
        self.assertFalse(self.user.is_deletion_pending())

    def get_formatted_national_number(self):
        nn = self.national_number
        if nn and len(nn) == 11:
            return f"{nn[:2]}.{nn[2:4]}.{nn[4:6]}-{nn[6:9]}.{nn[9:]}"
        return nn


class ValidationTestCase(TestCase):

    def test_validate_image_valid(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_file:
            image = Image.new('RGB', (100, 100))
            image.save(temp_file, format='JPEG')
            temp_file.seek(0)

            file = SimpleUploadedFile(temp_file.name, temp_file.read(), content_type='image/jpeg')
            try:
                validate_image(file)
            except ValidationError:
                self.fail("validate_image() raised ValidationError unexpectedly!")

    def test_validate_image_invalid_format(self):
        image = SimpleUploadedFile("test_image.txt", b"file_content", content_type="text/plain")
        with self.assertRaises(ValidationError):
            validate_image(image)

    def test_clean_email_valid(self):
        email = "valid@example.com"
        self.assertEqual(clean_email(email), email)

    def test_clean_email_invalid(self):
        email = "invalid-email"
        with self.assertRaises(ValidationError):
            clean_email(email)

    def test_sanitize_text(self):
        text = "<h1>Title</h1><script>alert('xss')</script>"
        sanitized_text = sanitize_text(text)
        self.assertEqual(sanitized_text, "Titlealertxss")

    def test_validate_national_number_valid(self):
        national_number = "12.03.05-789.01"
        self.assertEqual(validate_national_number(national_number), "12030578901")

    def test_validate_national_number_invalid_length(self):
        national_number = "1234567890"
        with self.assertRaises(ValidationError):
            validate_national_number(national_number)

    def test_validate_national_number_invalid_date(self):
        national_number = "99.99.99-999.99"
        with self.assertRaises(ValidationError):
            validate_national_number(national_number)

    def test_validate_password_valid(self):
        password = "StrongPass1"
        self.assertEqual(validate_password(password), password)

    def test_validate_password_invalid(self):
        password = "weak"
        with self.assertRaises(ValidationError):
            validate_password(password)

    def test_validate_telephone_valid(self):
        telephone = "+1234567890"
        self.assertEqual(validate_telephone(telephone), telephone)

    def test_validate_telephone_invalid(self):
        telephone = "invalid-phone"
        with self.assertRaises(ValidationError):
            validate_telephone(telephone)

class AvocatCaseModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='lawyer@example.com',
            first_name='Lawyer',
            last_name='One',
            password='password123',
            role='lawyer'
        )
        self.case = Case.objects.create(
            parent1=self.user,
            parent2=None,
            draft=False
        )
    def test_create_avocat_case(self):
        avocat_case = AvocatCase.objects.create(avocat=self.user, case=self.case)
        self.assertEqual(avocat_case.avocat.email, 'lawyer@example.com')
        self.assertEqual(avocat_case.case, self.case)

class JugeCaseModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='judge@example.com',
            first_name='Judge',
            last_name='One',
            password='password123',
            role='judge'
        )
        self.case = Case.objects.create(
            parent1=self.user,
            parent2=None,
            draft=False
        )

    def test_create_juge_case(self):
        juge_case = JugeCase.objects.create(juge=self.user, case=self.case)
        self.assertEqual(juge_case.juge.email, 'judge@example.com')
        self.assertEqual(juge_case.case, self.case)

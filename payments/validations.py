from django.core.exceptions import ValidationError
import magic


# validations.py
def validate_image(file):
    valid_mime_types = ['image/jpeg', 'image/png', 'image/gif']
    file_mime_type = magic.from_buffer(file.read(2048), mime=True)
    if file_mime_type not in valid_mime_types:
        raise ValidationError('Unsupported file type.')

    file.seek(0)  # Reset file pointer

